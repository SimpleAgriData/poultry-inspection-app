import { useState } from "react";
import { z } from "zod";
import Button from "@/components/button";
import Input from "@/components/input";
import PageSection from "@/components/page-section";
import { useHolding } from "@/contexts";
import type { Farm } from "@/services/api";

const SectionSchema = z.object({
	name: z.string().min(1),
});

export type SectionFormData = z.input<typeof SectionSchema>;

type SectionFormProps = {
	farm: Farm;
	submitText: string;
	onSubmit: (data: SectionFormData) => void;
	onValidate?: (valid: boolean) => void;
	initialData?: Partial<SectionFormData>;
};

export default function SectionForm(props: SectionFormProps) {
	const { holding, isLoading } = useHolding();
	const [formData, setFormData] = useState<SectionFormData>({
		name: props.initialData?.name || "",
	});

	const isFormValid = () => SectionSchema.safeParse(formData).success;

	const handleInputChange = <T extends keyof SectionFormData>(
		field: T,
		value: SectionFormData[T],
	) => {
		setFormData((prev) => ({ ...prev, [field]: value }));
		if (props.onValidate) {
			const result = SectionSchema.safeParse({ ...formData, [field]: value });
			props.onValidate(result.success);
		}
	};

	const onSubmit = () => {
		props.onSubmit(formData);
	};

	if (isLoading) {
		return <div>Lade Daten...</div>;
	}

	if (!holding) {
		return <div>Benutzer nicht authentifiziert.</div>;
	}

	return (
		<>
			<PageSection title={"Zugehörige Farm"}>
				<p className="font-medium">{props.farm.name}</p>
			</PageSection>
			<PageSection title="Allgemeine Informationen">
				<Input
					type="text"
					onChange={(value) => handleInputChange("name", value)}
					label="Bezeichner"
					placeholder="Bezeichner für das Abteil"
					value={formData.name}
					required={true}
				/>
			</PageSection>
			<Button type="primary" onClick={onSubmit} disabled={!isFormValid()} loaderOnClick={true}>
				{props.submitText}
			</Button>
		</>
	);
}
