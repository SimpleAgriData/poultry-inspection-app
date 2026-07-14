"use client";

import { useRouter } from "next/navigation";
import { type ReactNode, use, useEffect, useState } from "react";
import { submitChecklist } from "@/app/stallkarte/[stallkartenId]/check/[cycle]/submit";
import BasicForm from "@/components/basic-form";
import GenericLoaderPlaceholder from "@/components/generic-loader-placeholder";
import Input from "@/components/input";
import PageSection from "@/components/page-section";
import SubPageLayout from "@/components/sub-page-layout";
import { Subtitled } from "@/components/subtitled";
import ToggleSwitch from "@/components/toggle-switch";
import { useStallkarte } from "@/contexts/StallkarteContext";
import { todayUTC } from "@/services/dates";
import { getStallkarteChecklist } from "@/services/domain/stallkarte";
import { dateUtil } from "@/services/util/date-util";

export interface ChecklistFormData {
	didEmergencyPowerTest: boolean | null;
	didAlarmTest: boolean | null;
	didDarkPeriodTest: boolean | null;
	hadDivergenceDueToVet: boolean | null;
	didPestControlMeasures: boolean | null;
	pestControlMeasuresAnnotation: string | null;
	stableDisinfectionDate: Date | null;
	stableDisinfectant: string | null;
	stableDisinfectantDosis: string | null;
	siloCleaningDate: Date | null;
	siloCleaningDetergent: string | null;
	siloCleaningDosis: string | null;
	waterLineDisinfectionDate: Date | null;
	waterLineDisinfectant: string | null;
	waterLineDisinfectantDosis: string | null;
}

interface CheckListPageProps {
	params: Promise<{ cycle: string }>;
}

function SpacedInput({
	label,
	description,
	children,
}: {
	label: ReactNode;
	description?: ReactNode;
	children: ReactNode;
}) {
	return (
		<Subtitled subtitle={description}>
			<div className={"flex flex-row justify-between items-center"}>
				<p className={"font-medium"}>{label}</p>
				{children}
			</div>
		</Subtitled>
	);
}

export default function CheckListPage({ params }: CheckListPageProps) {
	const { cycle: cycleStr } = use(params);
	const { stallkarte, isLoading, refetch } = useStallkarte();
	const [cycle, setCycle] = useState<"rearing" | "fattening" | null>(null);
	const router = useRouter();
	const [formData, setFormData] = useState<ChecklistFormData>({
		didEmergencyPowerTest: null,
		didAlarmTest: null,
		didDarkPeriodTest: null,
		hadDivergenceDueToVet: null,
		didPestControlMeasures: null,
		pestControlMeasuresAnnotation: null,
		stableDisinfectionDate: null,
		stableDisinfectant: null,
		stableDisinfectantDosis: null,
		siloCleaningDate: null,
		siloCleaningDetergent: null,
		siloCleaningDosis: null,
		waterLineDisinfectionDate: null,
		waterLineDisinfectant: null,
		waterLineDisinfectantDosis: null,
	});

	const handleInputChange = <T extends keyof ChecklistFormData>(
		field: T,
		value: ChecklistFormData[T],
	) => {
		setFormData((prev) => ({
			...prev,
			[field]: value,
		}));
	};

	useEffect(() => {
		if (!stallkarte) return;
		if (cycleStr !== "rearing" && cycleStr !== "fattening") {
			router.replace(`/stallkarte/${stallkarte?.id}`);
			return;
		}
		setCycle(cycleStr);

		const checklist = getStallkarteChecklist(stallkarte.state, cycleStr);

		if (checklist) {
			setFormData({
				didEmergencyPowerTest: checklist.alarmTest?.didEmergencyPowerTest ?? null,
				didAlarmTest: checklist.alarmTest?.didAlarmTest ?? null,
				didDarkPeriodTest: checklist.lightingProgram?.didDarkPeriodTest ?? null,
				hadDivergenceDueToVet: checklist.lightingProgram?.hadDivergenceDueToVet ?? null,
				didPestControlMeasures: checklist.pestControlMeasures?.didPerformPestControl ?? null,
				pestControlMeasuresAnnotation: checklist.pestControlMeasures?.annotation ?? null,
				stableDisinfectionDate: checklist.stableDisinfection?.date ?? null,
				stableDisinfectant: checklist.stableDisinfection?.disinfectant ?? null,
				stableDisinfectantDosis: checklist.stableDisinfection?.dosis ?? null,
				siloCleaningDate: checklist.siloCleaned?.date ?? null,
				siloCleaningDetergent: checklist.siloCleaned?.detergent ?? null,
				siloCleaningDosis: checklist.siloCleaned?.dosis ?? null,
				waterLineDisinfectionDate: checklist.waterLineDisinfected?.date ?? null,
				waterLineDisinfectant: checklist.waterLineDisinfected?.disinfectant ?? null,
				waterLineDisinfectantDosis: checklist.waterLineDisinfected?.dosis ?? null,
			});
		}
	}, [cycleStr, stallkarte, router]);

	const onSubmit = async () => {
		if (!stallkarte || !cycle) return;

		const hasChanges = await submitChecklist(stallkarte, cycle, formData);
		if (hasChanges) {
			await refetch();
		}
		router.replace(`/stallkarte/${stallkarte.id}`);
	};

	if (isLoading || !stallkarte || !cycle) {
		return (
			<SubPageLayout title={`Serviceperiode`}>
				<GenericLoaderPlaceholder text={"Lade Stallkarte"} />
			</SubPageLayout>
		);
	}

	const todayPlaceholder = dateUtil.strDate(todayUTC());

	return (
		<SubPageLayout
			title={`Serviceperiode – ${cycle === "rearing" ? "Aufzucht" : "Mast"}`}
			subtitle={`Stallkarte ${stallkarte.state.fatteningCycle}`}
			backLink={`/stallkarte/${stallkarte.id}`}
		>
			<BasicForm
				submitText={"Speichern"}
				isDisabled={false}
				onSubmit={onSubmit}
				isReadOnly={stallkarte.state.isFinished}
			>
				<PageSection title={"Alarmtest"}>
					<SpacedInput label={"Notstromtest"}>
						<ToggleSwitch
							checked={formData.didEmergencyPowerTest ?? false}
							onChange={(v) => handleInputChange("didEmergencyPowerTest", v)}
						/>
					</SpacedInput>
					<SpacedInput label={"Alarmtest"}>
						<ToggleSwitch
							checked={formData.didAlarmTest ?? false}
							onChange={(v) => handleInputChange("didAlarmTest", v)}
						/>
					</SpacedInput>
				</PageSection>
				<PageSection title={"Lichtprogramm"}>
					<SpacedInput label={"Dunkelphase"} description={"Mindestens 8 Stunden ununterbrochen"}>
						<ToggleSwitch
							checked={formData.didDarkPeriodTest ?? false}
							onChange={(v) => handleInputChange("didDarkPeriodTest", v)}
						/>
					</SpacedInput>
					<SpacedInput
						label={"Abweichungen"}
						description={"Abweichungen aufgrund tierärztlicher Indikation"}
					>
						<ToggleSwitch
							checked={formData.hadDivergenceDueToVet ?? false}
							onChange={(v) => handleInputChange("hadDivergenceDueToVet", v)}
						/>
					</SpacedInput>
				</PageSection>

				<PageSection title={"Schädlingsbekämpfung"}>
					<SpacedInput
						label={"Durchgeführt"}
						description={"Bekämpfungsmaßnahmen gegen Schadnager, Käfer und Parasiten durchgeführt"}
					>
						<ToggleSwitch
							checked={formData.didPestControlMeasures ?? false}
							onChange={(v) => handleInputChange("didPestControlMeasures", v)}
						/>
					</SpacedInput>
					<Input
						type={"text"}
						label={"Anmerkungen"}
						placeholder={"z.B. Mittel"}
						value={formData.pestControlMeasuresAnnotation}
						onChange={(v) => handleInputChange("pestControlMeasuresAnnotation", v)}
					/>
				</PageSection>

				<PageSection title={"Stalldesinfektion"}>
					<Input
						type={"date"}
						label={"Datum"}
						options={{
							max: todayUTC(),
						}}
						placeholder={todayPlaceholder}
						value={formData.stableDisinfectionDate}
						onChange={(v) => handleInputChange("stableDisinfectionDate", v)}
					/>
					<div className="flex flex-col sm:flex-row space-y-6 sm:space-y-0 sm:space-x-4">
						<div className="flex-1">
							<Input
								type={"text"}
								label={"Mittel"}
								placeholder={"z.B. Mittel"}
								value={formData.stableDisinfectant ?? ""}
								onChange={(v) => handleInputChange("stableDisinfectant", v)}
							/>
						</div>
						<div className="flex-1">
							<Input
								type={"text"}
								label={"Dosis"}
								placeholder={"z.B. 3%"}
								value={formData.stableDisinfectantDosis ?? ""}
								onChange={(v) => handleInputChange("stableDisinfectantDosis", v)}
							/>
						</div>
					</div>
				</PageSection>

				<PageSection title={"Silo Reinigung"}>
					<Input
						type={"date"}
						label={"Datum"}
						options={{
							max: todayUTC(),
						}}
						placeholder={todayPlaceholder}
						value={formData.siloCleaningDate}
						onChange={(v) => handleInputChange("siloCleaningDate", v)}
					/>
					<div className="flex flex-col sm:flex-row space-y-6 sm:space-y-0 sm:space-x-4">
						<div className="flex-1">
							<Input
								type={"text"}
								label={"Mittel"}
								placeholder={"z.B. Mittel"}
								value={formData.siloCleaningDetergent ?? ""}
								onChange={(v) => handleInputChange("siloCleaningDetergent", v)}
							/>
						</div>
						<div className="flex-1">
							<Input
								type={"text"}
								label={"Dosis"}
								placeholder={"z.B. 3%"}
								value={formData.siloCleaningDosis ?? ""}
								onChange={(v) => handleInputChange("siloCleaningDosis", v)}
							/>
						</div>
					</div>
				</PageSection>

				<PageSection title={"TW Leitungsdesinfektion"}>
					<Input
						type={"date"}
						label={"Datum"}
						options={{
							max: todayUTC(),
						}}
						placeholder={todayPlaceholder}
						value={formData.waterLineDisinfectionDate}
						onChange={(v) => handleInputChange("waterLineDisinfectionDate", v)}
					/>
					<div className="flex flex-col sm:flex-row space-y-6 sm:space-y-0 sm:space-x-4">
						<div className="flex-1">
							<Input
								type={"text"}
								label={"Mittel"}
								placeholder={"z.B. Mittel"}
								value={formData.waterLineDisinfectant ?? ""}
								onChange={(v) => handleInputChange("waterLineDisinfectant", v)}
							/>
						</div>
						<div className="flex-1">
							<Input
								type={"text"}
								label={"Dosis"}
								placeholder={"z.B. 3%"}
								value={formData.waterLineDisinfectantDosis ?? ""}
								onChange={(v) => handleInputChange("waterLineDisinfectantDosis", v)}
							/>
						</div>
					</div>
				</PageSection>
			</BasicForm>
		</SubPageLayout>
	);
}
