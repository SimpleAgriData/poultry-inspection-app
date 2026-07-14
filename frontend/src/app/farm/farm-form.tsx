import { useState } from "react";
import { z } from "zod";
import BasicForm from "@/components/basic-form";
import Input from "@/components/input";
import PageSection from "@/components/page-section";
import Select from "@/components/select";
import type { Awaitable } from "@/services/awaitable";

const FarmTypeOptions = [
	{ label: "Aufzuchtfarm", value: "rearing" },
	{ label: "Mastfarm", value: "fattening" },
	{ label: "Kombifarm", value: "combined" },
];

const FarmSchema = z.object({
	name: z.string().min(1, "Farmname ist erforderlich"),
	type: z.enum(["rearing", "fattening", "combined"]),
	vvvoNumber: z
		.string()
		.min(1, "VVVO-Nummer ist erforderlich")
		.max(14, "VVVO-Nummer darf maximal 14 Zeichen lang sein"),
});

export type FarmFormData = z.infer<typeof FarmSchema>;

type FarmFormProps = {
	submitText: string;
	onSubmit: (data: FarmFormData) => Awaitable<void>;
	onValidate?: (valid: boolean) => void;
	initialData?: Partial<FarmFormData>;
};

export default function FarmForm(props: FarmFormProps) {
	const [formData, setFormData] = useState<FarmFormData>({
		name: props.initialData?.name || "",
		type: props.initialData?.type || "rearing",
		vvvoNumber: props.initialData?.vvvoNumber || "",
	});

	const isFormValid = () => FarmSchema.safeParse(formData).success;

	const handleInputChange = (field: keyof FarmFormData, value: string | null) => {
		if (value === null) return;

		setFormData((prev) => ({ ...prev, [field]: value }));
		if (props.onValidate) {
			const result = FarmSchema.safeParse({ ...formData, [field]: value });
			props.onValidate(result.success);
		}
	};

	const onSubmit = () => props.onSubmit(formData);

	return (
		<BasicForm submitText={props.submitText} isDisabled={!isFormValid()} onSubmit={onSubmit}>
			<PageSection title="Allgemeine Informationen">
				<Input
					type="text"
					onChange={(value) => handleInputChange("name", value)}
					label="Farmname"
					placeholder="Name der Farm"
					value={formData.name}
					required={true}
				/>
				<Select
					value={formData.type}
					onChange={(value) => handleInputChange("type", value)}
					options={FarmTypeOptions}
					label="Farmtyp"
					placeholder="Farmtyp auswählen"
					required={true}
				/>
				<Input
					type="text"
					onChange={(value) => handleInputChange("vvvoNumber", value)}
					label="VVVO-Nummer"
					placeholder="VVVO-Nummer der Farm"
					value={formData.vvvoNumber}
					required={true}
				/>
			</PageSection>
		</BasicForm>
	);
}
