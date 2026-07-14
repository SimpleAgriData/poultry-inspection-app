"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { MdAdd, MdDelete } from "react-icons/md";
import { z } from "zod";
import BasicForm from "@/components/basic-form";
import Button from "@/components/button";
import GenericLoaderPlaceholder from "@/components/generic-loader-placeholder";
import Input from "@/components/input";
import PageSection from "@/components/page-section";
import Select, { type SelectOption } from "@/components/select";
import SubPageLayout from "@/components/sub-page-layout";
import { useShallowStallkarten } from "@/contexts/ShallowStallkartenContext";
import { useStallkarte } from "@/contexts/StallkarteContext";
import { apiService } from "@/services/api";
import { todayUTC } from "@/services/dates";
import {
	FINISH_NOTE_TYPES,
	type FinishNoteEntry,
	type FinishNoteType,
	isCatchingFinishNoteType,
	isSlaughterFinishNoteType,
} from "@/services/domain/stallkarte";

const StallkarteFinishSchema = z.object({
	dateFinished: z.date(),
});

const finishNoteTypeOptions: SelectOption<FinishNoteType>[] = [
	{ value: FINISH_NOTE_TYPES[0], label: "Schlachtung" },
	{ value: FINISH_NOTE_TYPES[1], label: "Fangen" },
];

interface StallkarteFormData {
	dateFinished: Date | null;
	finishNotes: FinishNoteEntry[];
}

const createNoteId = (): string => {
	if (typeof crypto !== "undefined" && crypto.randomUUID) {
		return crypto.randomUUID();
	}
	return `finish-note-${Date.now()}-${Math.random().toString(16).slice(2)}`;
};

const createDefaultFinishNoteEntry = (noteType: FinishNoteType = "slaughter"): FinishNoteEntry => ({
	id: createNoteId(),
	noteType,
	noteText: null,
	deliveryReceiptNumber: null,
	batchNumber: null,
	vaccinationCode: null,
	treatmentCode: null,
	treatmentAmountValue: null,
	treatmentAmountUnit: null,
	treatmentWaitingTimeValue: null,
	treatmentWaitingTimeUnit: null,
	sockTestResult: null,
	slaughterDate: null,
	slaughterAnimalsCount: null,
	slaughterFinalWeightKg: null,
	slaughtererName: null,
	catchingTime: null,
	catcherName: null,
});

const isNoteComplete = (note: FinishNoteEntry): boolean => {
	if (isSlaughterFinishNoteType(note.noteType)) {
		return (
			note.slaughterDate !== null &&
			note.slaughterAnimalsCount !== null &&
			note.slaughterAnimalsCount >= 0 &&
			note.slaughterFinalWeightKg !== null &&
			note.slaughterFinalWeightKg >= 0 &&
			note.slaughtererName !== null &&
			note.slaughtererName.trim() !== ""
		);
	}

	if (isCatchingFinishNoteType(note.noteType)) {
		return (
			note.catchingTime !== null &&
			note.catchingTime.trim() !== "" &&
			note.catcherName !== null &&
			note.catcherName.trim() !== ""
		);
	}

	return false;
};

export default function FinishPage() {
	const { refetch: refetchShallowStallkarten } = useShallowStallkarten();
	const { stallkarte, refetch } = useStallkarte();
	const [saving, setSaving] = useState(false);
	const [formData, setFormData] = useState<StallkarteFormData>({
		dateFinished: todayUTC(),
		finishNotes: [],
	});
	const router = useRouter();

	useEffect(() => {
		if (!stallkarte) {
			return;
		}

		setFormData((prev) => ({
			...prev,
			finishNotes: stallkarte.state.finishNotes,
		}));
	}, [stallkarte]);

	const updateField = <K extends keyof StallkarteFormData>(
		field: K,
		value: StallkarteFormData[K],
	) => {
		setFormData((prev) => ({ ...prev, [field]: value }));
	};

	const updateFinishNote = (id: string, next: FinishNoteEntry) => {
		updateField(
			"finishNotes",
			formData.finishNotes.map((note) => (note.id === id ? next : note)),
		);
	};

	const updateFinishNoteType = (id: string, type: FinishNoteType) => {
		const current = formData.finishNotes.find((note) => note.id === id);
		if (!current) {
			return;
		}

		updateFinishNote(id, {
			...current,
			noteType: type,
			slaughterDate: null,
			slaughterAnimalsCount: null,
			slaughterFinalWeightKg: null,
			slaughtererName: null,
			catchingTime: null,
			catcherName: null,
		});
	};

	const addFinishNote = () => {
		updateField("finishNotes", [...formData.finishNotes, createDefaultFinishNoteEntry()]);
	};

	const removeFinishNote = (id: string) => {
		updateField(
			"finishNotes",
			formData.finishNotes.filter((note) => note.id !== id),
		);
	};

	const isFormValid = () => {
		const result = StallkarteFinishSchema.safeParse(formData);
		if (!result.success) {
			return false;
		}

		return formData.finishNotes.every(isNoteComplete);
	};

	const handleSave = async () => {
		if (!stallkarte || saving) return;

		setSaving(true);
		try {
			await apiService.stallkarte.runCommand("save-finish-notes", {
				stallkarteId: stallkarte.id,
				finishNotes: formData.finishNotes,
			});
			await refetch();
		} finally {
			setSaving(false);
		}
	};

	const handleSubmit = async () => {
		if (!stallkarte) return;

		const result = StallkarteFinishSchema.safeParse(formData);
		if (!result.success) return;
		if (!formData.finishNotes.every(isNoteComplete)) return;

		await apiService.stallkarte.runCommand("finish-stallkarte", {
			stallkarteId: stallkarte.id,
			dateFinished: result.data.dateFinished,
			finishNotes: formData.finishNotes,
		});
		await Promise.all([refetch(), refetchShallowStallkarten()]);

		router.push(`/stallkarten`);
	};

	if (!stallkarte) {
		return (
			<SubPageLayout title={"Stallkarte abschließen"}>
				<GenericLoaderPlaceholder text={"Lade Stallkarte"} />
			</SubPageLayout>
		);
	}

	return (
		<SubPageLayout title={"Stallkarte abschließen"} backLink={`/stallkarte/${stallkarte.id}`}>
			<BasicForm
				submitText={"Abschließen"}
				isDisabled={!isFormValid()}
				onSubmit={handleSubmit}
				isReadOnly={stallkarte.state.isFinished}
			>
				<PageSection title={"Details"}>
					<Input
						type={"date"}
						label={"Abschlussdatum"}
						onChange={(v) => updateField("dateFinished", v)}
						value={formData.dateFinished}
					/>
					<p>Beim Abschließen müssen Fangen- und Schlachtdaten dokumentiert werden.</p>
				</PageSection>

				<PageSection title={"Fangen und Schlachtung"} noBodyStyle={true}>
					<div className="space-y-2">
						{formData.finishNotes.map((note) => (
							<div
								key={note.id}
								className="w-full bg-surface-container rounded-lg shadow-md p-3 space-y-3"
							>
								<div className="flex items-center gap-2">
									<div className="ml-auto">
										<Button
											type="link"
											width="auto"
											iconLeft={<MdDelete />}
											onClick={() => removeFinishNote(note.id)}
										>
											Entfernen
										</Button>
									</div>
								</div>

								<Select
									label="Ereignistyp"
									value={note.noteType}
									onChange={(v) => updateFinishNoteType(note.id, v as FinishNoteType)}
									options={finishNoteTypeOptions}
									required={true}
								/>

								{isSlaughterFinishNoteType(note.noteType) && (
									<>
										<Input
											type="date"
											label="Schlachtdatum"
											value={note.slaughterDate}
											onChange={(v) =>
												updateFinishNote(note.id, {
													...note,
													slaughterDate: v,
												})
											}
											required={true}
										/>
										<Input
											type="number"
											label="Stückzahl"
											value={note.slaughterAnimalsCount}
											onChange={(v) =>
												updateFinishNote(note.id, {
													...note,
													slaughterAnimalsCount: v,
												})
											}
											options={{ min: 0 }}
											required={true}
										/>
										<Input
											type="number"
											label="Endgewicht (kg)"
											value={note.slaughterFinalWeightKg}
											onChange={(v) =>
												updateFinishNote(note.id, {
													...note,
													slaughterFinalWeightKg: v,
												})
											}
											options={{ min: 0 }}
											required={true}
										/>
										<Input
											type="text"
											label="Schlachter"
											value={note.slaughtererName}
											onChange={(v) =>
												updateFinishNote(note.id, {
													...note,
													slaughtererName: v,
												})
											}
											placeholder="z.B. Steinfelder"
											required={true}
										/>
									</>
								)}

								{isCatchingFinishNoteType(note.noteType) && (
									<>
										<Input
											type="time"
											label="Uhrzeit"
											value={note.catchingTime}
											onChange={(v) =>
												updateFinishNote(note.id, {
													...note,
													catchingTime: v,
												})
											}
											required={true}
										/>
										<Input
											type="text"
											label="Fänger"
											value={note.catcherName}
											onChange={(v) =>
												updateFinishNote(note.id, {
													...note,
													catcherName: v,
												})
											}
											placeholder="z.B. Team Nord"
											required={true}
										/>
									</>
								)}
							</div>
						))}

						<Button type="primary" iconLeft={<MdAdd size={"1.5em"} />} onClick={addFinishNote}>
							Notiz hinzufügen
						</Button>

						<Button type="secondary" onClick={handleSave} withLoader={saving}>
							Notizen speichern
						</Button>
					</div>
				</PageSection>
			</BasicForm>
		</SubPageLayout>
	);
}
