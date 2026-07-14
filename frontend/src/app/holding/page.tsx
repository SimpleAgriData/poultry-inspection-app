"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { z } from "zod";
import BasicForm from "@/components/basic-form";
import GenericLoaderPlaceholder from "@/components/generic-loader-placeholder";
import Input from "@/components/input";
import PageSection from "@/components/page-section";
import SubPageLayout from "@/components/sub-page-layout";
import { useHolding } from "@/contexts";
import { apiService } from "@/services/api";

// TODO: This is a duplicate of the onboarding schema. Should be refactored to a shared schema.
const HoldingSchema = z.object({
	name: z.string().min(1, "Betriebsname ist erforderlich").trim(),
	street: z.string().min(1, "Straße ist erforderlich").trim(),
	zipCode: z.string().min(1, "PLZ ist erforderlich").trim(),
	city: z.string().min(1, "Ort ist erforderlich").trim(),
	ecoControlNr: z.string().min(1, "Öko-Kontrollnummer ist erforderlich").trim(),
	hatchery: z.string().min(1, "Brüterei ist erforderlich").trim(),
	breedName: z.string().min(1, "Tierrasse ist erforderlich").trim(),
});

type HoldingFormData = z.infer<typeof HoldingSchema>;

export default function HoldingPage() {
	const { holding, refetch } = useHolding();
	const [formData, setFormData] = useState<HoldingFormData>({
		name: "",
		street: "",
		zipCode: "",
		city: "",
		ecoControlNr: "",
		hatchery: "",
		breedName: "",
	});
	const router = useRouter();

	useEffect(() => {
		if (holding) {
			setFormData({
				name: holding.name,
				street: holding.addressStreet,
				zipCode: holding.addressZip,
				city: holding.addressCity,
				ecoControlNr: holding.ecoControlNumber,
				hatchery: holding.hatchery,
				breedName: holding.breed,
			});
		}
	}, [holding]);

	const isFormValid = () => HoldingSchema.safeParse(formData).success;

	const handleInputChange = (field: keyof HoldingFormData, value: string | null) => {
		if (value === null) return;

		setFormData((prev) => ({ ...prev, [field]: value }));
	};

	const onSubmit = async () => {
		if (!holding) return;
		const result = HoldingSchema.safeParse(formData);
		if (result.success) {
			await apiService.updateHolding({
				name: formData.name,
				addressStreet: formData.street,
				addressZip: formData.zipCode,
				addressCity: formData.city,
				ecoControlNumber: formData.ecoControlNr,
				hatchery: formData.hatchery,
				breed: formData.breedName,
				holdingId: holding.id,
			});
			await refetch();
			router.back();
		}
	};

	if (!holding) {
		return (
			<SubPageLayout title="Betrieb bearbeiten" backLink={"/overview"}>
				<GenericLoaderPlaceholder />
			</SubPageLayout>
		);
	}

	return (
		<SubPageLayout title="Betriebsdaten bearbeiten" backLink={"/overview"}>
			<BasicForm
				submitText={"Änderungen Speichern"}
				isDisabled={!isFormValid()}
				onSubmit={onSubmit}
			>
				<PageSection title="Allgemeine Informationen">
					<Input
						type="text"
						onChange={(value) => handleInputChange("name", value)}
						label="Betriebsname"
						placeholder="Musterbetrieb"
						value={formData.name}
					/>
					<Input
						type="text"
						onChange={(value) => handleInputChange("street", value)}
						label="Straße und Hausnummer"
						placeholder="Musterstraße 1"
						value={formData.street}
					/>
					<div className="flex space-x-4">
						<div className="w-1/3">
							<Input
								label="PLZ"
								placeholder="12345"
								type="text"
								inputMode={"numeric"}
								value={formData.zipCode}
								onChange={(value) => handleInputChange("zipCode", value)}
							/>
						</div>
						<div className="flex-1">
							<Input
								label="Ort"
								placeholder="Musterstadt"
								type="text"
								value={formData.city}
								onChange={(value) => handleInputChange("city", value)}
							/>
						</div>
					</div>
				</PageSection>
				<PageSection title="Weitere Angaben">
					<Input
						type="text"
						onChange={(value) => handleInputChange("ecoControlNr", value)}
						label="Öko-Kontrollnummer"
						placeholder="DE-ÖKO-123"
						value={formData.ecoControlNr}
					/>
					<Input
						type="text"
						onChange={(value) => handleInputChange("hatchery", value)}
						label="Brüterei"
						placeholder="Musterbrüterei"
						value={formData.hatchery}
					/>
					<Input
						type="text"
						onChange={(value) => handleInputChange("breedName", value)}
						label="Tierrasse"
						placeholder="Muster-Rasse"
						value={formData.breedName}
					/>
				</PageSection>
			</BasicForm>
		</SubPageLayout>
	);
}
