"use client";

import { useParams, useRouter } from "next/navigation";
import type React from "react";
import { useCallback, useEffect, useState } from "react";
import GeneralView, {
	type GeneralFormData,
} from "@/app/stallkarte/[stallkartenId]/day/[productionDay]/general-view";
import SectionView, {
	type SectionFormData,
} from "@/app/stallkarte/[stallkartenId]/day/[productionDay]/section-view";
import {
	type DayFormData,
	submitDayFormData,
} from "@/app/stallkarte/[stallkartenId]/day/[productionDay]/submit";
import Button from "@/components/button";
import SubPageLayout from "@/components/sub-page-layout";
import Tabs, { type TabItem } from "@/components/tabs";
import { useStallkarte } from "@/contexts/StallkarteContext";
import {
	type GeneralNoteEntry,
	getDateOfProductionDay,
	getStallkarteFarmOfDay,
	isSockTestNoteType,
	isTreatmentNoteType,
	isVaccinationNoteType,
	SOCK_TEST_RESULTS,
	type StallkarteSection,
	type StallkarteStateDaySection,
	TREATMENT_AMOUNT_UNITS,
	TREATMENT_CODES,
	VACCINATION_CODES,
	WAITING_TIME_UNITS,
} from "@/services/domain/stallkarte";

interface Tab extends TabItem {
	view: React.ReactNode;
	id: string;
}

type Params = {
	productionDay: string;
};

const createNoteId = (): string => {
	if (typeof crypto !== "undefined" && crypto.randomUUID) {
		return crypto.randomUUID();
	}
	return `note-${Date.now()}-${Math.random().toString(16).slice(2)}`;
};

const normalizeNote = (note: GeneralNoteEntry): GeneralNoteEntry => {
	const hasId = Boolean(note.id);
	const normalized: GeneralNoteEntry = {
		...note,
		id: note.id || createNoteId(),
		isDirty: !hasId,
		noteText: note.noteText,
	};

	if (isVaccinationNoteType(note.noteType)) {
		normalized.vaccinationCode = note.vaccinationCode ?? VACCINATION_CODES[0];
	}

	if (isTreatmentNoteType(note.noteType)) {
		normalized.treatmentCode = note.treatmentCode ?? TREATMENT_CODES[0];
		normalized.treatmentAmountUnit = note.treatmentAmountUnit ?? TREATMENT_AMOUNT_UNITS[0];
		normalized.treatmentWaitingTimeUnit = note.treatmentWaitingTimeUnit ?? WAITING_TIME_UNITS[0];
	}

	if (isSockTestNoteType(note.noteType)) {
		normalized.sockTestResult = note.sockTestResult ?? SOCK_TEST_RESULTS[1];
	}

	return normalized;
};

export default function NewDayPage() {
	const [submitting, setSubmitting] = useState(false);
	const { stallkarte, refetch } = useStallkarte();
	const [formData, setFormData] = useState<DayFormData | null>(null);
	const [tabIndex, setTabIndex] = useState(0);
	const router = useRouter();
	const { productionDay: productionDayStr } = useParams<Params>();
	const productionDay = parseInt(productionDayStr, 10);

	useEffect(() => {
		if (Number.isNaN(productionDay) || !stallkarte) {
			return;
		}

		const initialData = stallkarte.state.days[productionDay];
		const farm = getStallkarteFarmOfDay(stallkarte, productionDay);

		const initialGeneralData: GeneralFormData = {
			temperatureCelsius: initialData?.temperatureCelsius ?? null,
			humidityPercent: initialData?.humidityPercent ?? null,
			weightGrams: initialData?.weightGrams ?? null,
			feedConsumptionKg: initialData?.feedConsumptionKg ?? null,
			waterConsumptionLiters: initialData?.waterConsumptionLiters ?? null,
			openingTime: initialData?.openingTime ?? null,
			weatherConditions: initialData?.weatherConditions ?? [],
			veterinarian: initialData?.veterinarian ?? false,
			notes: (initialData?.notes ?? []).map(normalizeNote),
		};

		const initialSections: Record<number, SectionFormData> = {};
		for (const section of farm?.sections ?? []) {
			const sectionData: StallkarteStateDaySection | undefined =
				initialData?.sections[section.number];
			initialSections[section.number] = {
				selectiveMortalityMorning: sectionData?.selectiveMortalityMorning ?? null,
				naturalMortalityMorning: sectionData?.naturalMortalityMorning ?? null,
				selectiveMortalityEvening: sectionData?.selectiveMortalityEvening ?? null,
				naturalMortalityEvening: sectionData?.naturalMortalityEvening ?? null,
				note: sectionData?.note ?? null,
			};
		}

		setFormData({
			general: initialGeneralData,
			sections: initialSections,
		});
	}, [stallkarte, productionDay]);

	const onSectionChange = useCallback(
		(section: StallkarteSection, sectionFormData: SectionFormData) => {
			if (stallkarte?.state.isFinished) {
				return;
			}
			setFormData((prev) => {
				if (!prev) {
					return prev;
				}

				if (prev.sections[section.number] === sectionFormData) {
					return prev;
				}

				return {
					...prev,
					sections: {
						...prev.sections,
						[section.number]: sectionFormData,
					},
				};
			});
		},
		[stallkarte?.state.isFinished],
	);

	const onGeneralChange = useCallback(
		(generalFormData: GeneralFormData) => {
			if (stallkarte?.state.isFinished) {
				return;
			}
			setFormData((prev) => {
				if (!prev) {
					return prev;
				}

				if (prev.general === generalFormData) {
					return prev;
				}

				return {
					...prev,
					general: generalFormData,
				};
			});
		},
		[stallkarte?.state.isFinished],
	);

	if (Number.isNaN(productionDay)) {
		return null;
	}

	if (!stallkarte) {
		return null;
	}

	if (!formData) {
		return null;
	}

	const onSubmit = async () => {
		if (stallkarte.state.isFinished) {
			return;
		}
		if (submitting) return;

		setSubmitting(true);
		try {
			await submitDayFormData(stallkarte, productionDay, formData);
			await refetch();
			router.back();
		} finally {
			setSubmitting(false);
		}
	};

	const farm = getStallkarteFarmOfDay(stallkarte, productionDay);
	const transferDay = stallkarte.state.transfer?.productionDay ?? null;
	const isFatteningDay = transferDay !== null && productionDay >= transferDay;
	const sectionTabs: Tab[] = [];

	for (const s of farm?.sections || []) {
		const sectionFormData = formData.sections[s.number] ?? {
			selectiveMortalityMorning: null,
			naturalMortalityMorning: null,
			selectiveMortalityEvening: null,
			naturalMortalityEvening: null,
			note: null,
		};
		sectionTabs.push({
			id: s.id.toString(),
			title: s.name,
			view: (
				<SectionView
					value={sectionFormData}
					onChange={(next) => onSectionChange(s, next)}
					disabled={stallkarte.state.isFinished}
				/>
			),
		});
	}

	const generalTab = {
		title: "Allgemein",
		id: "general",
		view: (
			<GeneralView
				value={formData.general}
				showFatteningSection={isFatteningDay}
				onChange={onGeneralChange}
				disabled={stallkarte.state.isFinished}
			/>
		),
	} satisfies Tab;

	const tabs: Tab[] = [generalTab, ...sectionTabs];
	const dateFormatted = new Intl.DateTimeFormat("de-DE", {
		year: "numeric",
		month: "2-digit",
		day: "2-digit",
	}).format(getDateOfProductionDay(stallkarte.state, productionDay));

	return (
		<div className={"flex flex-col h-full"}>
			<div className={"flex-1 min-h-0"}>
				<SubPageLayout
					title={`Tag ${productionDay} protokollieren`}
					subtitle={`${dateFormatted} – Stallkarte ${stallkarte?.state.fatteningCycle}`}
				>
					<div className={"w-full shrink-0"}>
						<Tabs
							align={"center"}
							tabs={tabs}
							activeTabIndex={tabIndex}
							onTabChange={setTabIndex}
						/>
					</div>

					<div className="w-full flex-1">
						<div className={"flex flex-row gap-10 overflow-x-hidden"}>
							{tabs.map((tab, index) => (
								<div
									key={tab.id}
									className={`block w-full shrink-0
															${tabIndex === index ? "" : "hidden"}`}
								>
									{tab.view}
								</div>
							))}
						</div>
					</div>
				</SubPageLayout>
			</div>
			{!stallkarte.state.isFinished && (
				<div
					className={
						"w-full bg-surface-container shadow-[0_2px_5px] shadow-black flex justify-center"
					}
				>
					<div className={"w-full max-w-md p-4"}>
						<Button type="primary" width={"full"} onClick={onSubmit} withLoader={submitting}>
							Tag speichern
						</Button>
					</div>
				</div>
			)}
		</div>
	);
}
