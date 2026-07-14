"use client";

import { MdWarning } from "react-icons/md";
import Input from "@/components/input";
import PageSection from "@/components/page-section";
import { StyledLabel } from "@/components/styled-label";
import TextArea from "@/components/text-area";

export interface SectionFormData {
	naturalMortalityMorning: number | null;
	selectiveMortalityMorning: number | null;
	naturalMortalityEvening: number | null;
	selectiveMortalityEvening: number | null;
	note: string | null;
}

interface SectionViewProps {
	value: SectionFormData;
	onChange: (value: SectionFormData) => void;
	disabled?: boolean;
}

export default function SectionView({ value, onChange, disabled = false }: SectionViewProps) {
	const formData = value;

	const updateField = <K extends keyof SectionFormData>(field: K, value: SectionFormData[K]) => {
		onChange({ ...formData, [field]: value });
	};

	const isMorningFinished =
		formData.naturalMortalityMorning !== null && formData.selectiveMortalityMorning !== null;
	const isEveningFinished =
		formData.naturalMortalityEvening !== null && formData.selectiveMortalityEvening !== null;

	return (
		<div className={"space-y-6"}>
			<PageSection
				title={
					<div className={"flex flex-row items-center gap-2 w-full"}>
						Kontrollgang – Morgens
						{!isMorningFinished && (
							<StyledLabel className={"ml-auto"} type={"warning"} icon={<MdWarning />}>
								Unvollständig
							</StyledLabel>
						)}
					</div>
				}
			>
				<div className="flex flex-col sm:flex-row space-y-6 sm:space-y-0 sm:space-x-4">
					<div className="flex-1">
						<Input
							type="number"
							label="Natürliche Verluste"
							value={formData.naturalMortalityMorning}
							onChange={(value) => updateField("naturalMortalityMorning", value)}
							placeholder="z.B. 1"
							disabled={disabled}
						/>
					</div>
					<div className="flex-1">
						<Input
							type="number"
							label="Selektive Verluste"
							value={formData.selectiveMortalityMorning}
							onChange={(value) => updateField("selectiveMortalityMorning", value)}
							placeholder="z.B. 0"
							disabled={disabled}
						/>
					</div>
				</div>
			</PageSection>
			<PageSection
				title={
					<div className={"flex flex-row items-center gap-2 w-full"}>
						Kontrollgang – Abends
						{!isEveningFinished && (
							<StyledLabel className={"ml-auto"} type={"warning"} icon={<MdWarning />}>
								Unvollständig
							</StyledLabel>
						)}
					</div>
				}
			>
				<div className="flex flex-col sm:flex-row space-y-6 sm:space-y-0 sm:space-x-4">
					<div className="flex-1">
						<Input
							type="number"
							label="Natürliche Verluste"
							value={formData.naturalMortalityEvening}
							onChange={(value) => updateField("naturalMortalityEvening", value)}
							placeholder="z.B. 2"
							disabled={disabled}
						/>
					</div>
					<div className="flex-1">
						<Input
							type="number"
							label="Selektive Verluste"
							value={formData.selectiveMortalityEvening}
							onChange={(value) => updateField("selectiveMortalityEvening", value)}
							placeholder="z.B. 1"
							disabled={disabled}
						/>
					</div>
				</div>
			</PageSection>
			<PageSection title={"Sonstiges"}>
				<TextArea
					value={formData.note || ""}
					label={"Bemerkung"}
					onChange={(value) => updateField("note", value)}
					placeholder={"z.B. Auffälligkeiten, besondere Vorkommnisse, etc."}
					disabled={disabled}
				/>
			</PageSection>
		</div>
	);
}
