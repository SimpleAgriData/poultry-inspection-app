"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { z } from "zod";
import { fatteningFarmOptions, rearingFarmOptions } from "@/app/stallkarte/farm-options";
import BasicForm from "@/components/basic-form";
import GenericLoaderPlaceholder from "@/components/generic-loader-placeholder";
import { InfoBanner } from "@/components/info-banner";
import Input from "@/components/input";
import PageSection from "@/components/page-section";
import Select from "@/components/select";
import SubPageLayout from "@/components/sub-page-layout";
import ToggleSwitch from "@/components/toggle-switch";
import { useHolding } from "@/contexts";
import { useShallowStallkarten } from "@/contexts/ShallowStallkartenContext";
import { apiService } from "@/services/api";
import { todayUTC } from "@/services/dates";

const StallkarteSchema = z.object({
	rearingFarm: z.number().min(1, "Aufzuchtfarm ist erforderlich"),
	fatteningFarm: z.number().nullable(), // Optional
	dateStarted: z.date(),
	dateHatched: z.date(),
	hatchery: z.string().min(1, "Brüterei ist erforderlich"),
	breed: z.string().min(1, "Rasse ist erforderlich"),
	fatteningCycle: z.string().min(1, "Mastdurchgang ist erforderlich"),
	euOrganic: z.boolean(),
	naturland: z.boolean(),
});

const ParentFlockSchema = z.object({
	herdIdentifier: z.string().min(1, "Elterntier-Herde ist erforderlich"),
	productionWeek: z.number().min(1, "Produktionswoche muss größer als 0 sein"),
});

const InstallationSectionSchema = z.object({
	initialAnimalsCount: z.number().min(1, "Tierzahl muss größer als 0 sein"),
	initialWeightGrams: z.number().min(1, "Gewicht muss größer als 0 sein"),
	parentFlocks: z.array(ParentFlockSchema).min(1, "Mindestens ein ET/PW-Eintrag ist erforderlich"),
});

const InstallationSchema = z.object({
	bedding: z.string().trim().min(1, "Einstreu ist erforderlich"),
});

type ParentFlockFormData = {
	id: string;
	herdIdentifier: string;
	productionWeek: number | null;
};

type InstallationSectionFormData = {
	initialAnimalsCount: number | null;
	initialWeightGrams: number | null;
	parentFlocks: ParentFlockFormData[];
};

const createParentFlockId = (): string => {
	if (typeof crypto !== "undefined" && crypto.randomUUID) {
		return crypto.randomUUID();
	}

	return `parent-flock-${Date.now()}-${Math.random().toString(16).slice(2)}`;
};

const yesterdayUTC = (): Date => {
	const date = todayUTC();
	date.setUTCDate(date.getUTCDate() - 1);
	return date;
};

interface FormData {
	rearingFarm: number | null;
	fatteningFarm: number | null;
	dateStarted: Date | null;
	dateHatched: Date | null;
	hatchery: string;
	breed: string;
	fatteningCycle: string;
	euOrganic: boolean;
	naturland: boolean;
	installationBedding: string;
	installationBySectionNumber: Record<number, InstallationSectionFormData>;
}

export default function NewStallkartePage() {
	const router = useRouter();
	const { holding, isLoading } = useHolding();
	const { refetch } = useShallowStallkarten();
	const [formData, setFormData] = useState<FormData>({
		rearingFarm: null,
		fatteningFarm: null,
		dateHatched: yesterdayUTC(),
		dateStarted: todayUTC(),
		hatchery: "",
		breed: "",
		fatteningCycle: "",
		euOrganic: true,
		naturland: true,
		installationBedding: "",
		installationBySectionNumber: {},
	});

	const updateField = <K extends keyof FormData>(field: K, value: FormData[K]) => {
		setFormData((prev) => ({ ...prev, [field]: value }));
	};

	const updateInstallationSection = (sectionNumber: number, next: InstallationSectionFormData) => {
		setFormData((prev) => ({
			...prev,
			installationBySectionNumber: {
				...prev.installationBySectionNumber,
				[sectionNumber]: next,
			},
		}));
	};

	const selectedRearingFarm =
		holding?.farms.find((farm) => farm.id === formData.rearingFarm) ?? null;
	const selectedSections = selectedRearingFarm?.sections ?? [];

	useEffect(() => {
		if (!selectedRearingFarm) {
			setFormData((prev) => ({ ...prev, installationBySectionNumber: {} }));
			return;
		}

		setFormData((prev) => {
			const nextInstallationBySectionNumber: Record<number, InstallationSectionFormData> = {};
			for (const [index] of selectedRearingFarm.sections.entries()) {
				const sectionNumber = index + 1;
				nextInstallationBySectionNumber[sectionNumber] = prev.installationBySectionNumber[
					sectionNumber
				] ?? {
					initialAnimalsCount: null,
					initialWeightGrams: null,
					parentFlocks: [
						{
							id: createParentFlockId(),
							herdIdentifier: "",
							productionWeek: null,
						},
					],
				};
			}

			return {
				...prev,
				installationBySectionNumber: nextInstallationBySectionNumber,
			};
		});
	}, [selectedRearingFarm]);

	const isInstallationValid = (): boolean => {
		if (!InstallationSchema.safeParse({ bedding: formData.installationBedding }).success) {
			return false;
		}

		if (selectedSections.length === 0) {
			return false;
		}

		return selectedSections.every((_, index) => {
			const sectionNumber = index + 1;
			const sectionData = formData.installationBySectionNumber[sectionNumber];
			if (!sectionData) {
				return false;
			}

			const parsed = InstallationSectionSchema.safeParse({
				initialAnimalsCount: sectionData.initialAnimalsCount,
				initialWeightGrams: sectionData.initialWeightGrams,
				parentFlocks: sectionData.parentFlocks.map((entry) => ({
					herdIdentifier: entry.herdIdentifier,
					productionWeek: entry.productionWeek,
				})),
			});

			return parsed.success;
		});
	};

	const isFormValid = (): boolean => {
		try {
			StallkarteSchema.parse(formData);
			return isInstallationValid();
		} catch (_error) {
			return false;
		}
	};

	const getValidationErrors = (): string[] => {
		const errors: string[] = [];

		const baseValidation = StallkarteSchema.safeParse(formData);
		if (!baseValidation.success) {
			const fieldLabelByPath: Partial<Record<keyof FormData, string>> = {
				rearingFarm: "Aufzuchtfarm ist erforderlich",
				fatteningFarm: "Mastfarm ist ungültig",
				dateStarted: "Einstallungsdatum ist erforderlich",
				dateHatched: "Schlupfdatum ist erforderlich",
				hatchery: "Brüterei ist erforderlich",
				breed: "Rasse ist erforderlich",
				fatteningCycle: "Mastdurchgang ist erforderlich",
			};

			for (const issue of baseValidation.error.issues) {
				const path = issue.path[0] as keyof FormData | undefined;
				if (path && fieldLabelByPath[path]) {
					errors.push(fieldLabelByPath[path]);
					continue;
				}
				errors.push(issue.message);
			}
		}

		if (!InstallationSchema.safeParse({ bedding: formData.installationBedding }).success) {
			errors.push("Einstreu ist erforderlich");
		}

		if (selectedSections.length === 0) {
			errors.push("Mindestens ein Abteil in der Aufzuchtfarm ist erforderlich");
			return [...new Set(errors)];
		}

		for (const [index] of selectedSections.entries()) {
			const sectionNumber = index + 1;
			const sectionData = formData.installationBySectionNumber[sectionNumber];
			if (!sectionData) {
				errors.push(`Abteil ${sectionNumber}: Einstallungsdaten fehlen`);
				continue;
			}

			if ((sectionData.initialAnimalsCount ?? 0) <= 0) {
				errors.push(`Abteil ${sectionNumber}: Tieranzahl muss größer als 0 sein`);
			}

			if ((sectionData.initialWeightGrams ?? 0) <= 0) {
				errors.push(`Abteil ${sectionNumber}: Gewicht muss größer als 0 sein`);
			}

			if (sectionData.parentFlocks.length === 0) {
				errors.push(`Abteil ${sectionNumber}: Mindestens ein ET/PW-Eintrag ist erforderlich`);
			}

			for (const [parentFlockIndex, parentFlock] of sectionData.parentFlocks.entries()) {
				if (parentFlock.herdIdentifier.trim() === "") {
					errors.push(
						`Abteil ${sectionNumber}, ET/PW ${parentFlockIndex + 1}: Elterntier-Herde ist erforderlich`,
					);
				}

				if ((parentFlock.productionWeek ?? 0) <= 0) {
					errors.push(
						`Abteil ${sectionNumber}, ET/PW ${parentFlockIndex + 1}: Produktionswoche muss größer als 0 sein`,
					);
				}
			}
		}

		return [...new Set(errors)];
	};

	const onSubmit = async () => {
		if (!holding) return;
		const result = StallkarteSchema.safeParse(formData);
		if (!result.success) {
			console.error("Validation failed:", result.error);
			return;
		}
		const validatedData = result.data;

		const response = await apiService.stallkarte.runCommand("start-stallkarte", {
			dateHatched: validatedData.dateHatched,
			dateStarted: validatedData.dateStarted,
			hatcheryName: validatedData.hatchery,
			breed: validatedData.breed,
			fatteningCycle: validatedData.fatteningCycle,
			ecoControlNumber: holding.ecoControlNumber,
			isEuBio: validatedData.euOrganic,
			isNaturland: validatedData.naturland,
		});
		const stallkarte = await apiService.stallkarte.getStallkarte(response.stallkarte_id);
		if (!stallkarte) {
			throw new Error("Stallkarte konnte nicht geladen werden");
		}

		await apiService.stallkarte.runCommand("assign-rearing-farm", {
			stallkarteId: stallkarte.id,
			farmId: validatedData.rearingFarm,
		});
		if (validatedData.fatteningFarm) {
			await apiService.stallkarte.runCommand("assign-fattening-farm", {
				stallkarteId: stallkarte.id,
				farmId: validatedData.fatteningFarm,
			});
		}

		const sectionDetails = selectedSections.map((_, index) => {
			const sectionNumber = index + 1;
			const sectionData = formData.installationBySectionNumber[sectionNumber];
			if (!sectionData) {
				throw new Error(`Einstallungsdaten für Abteil ${sectionNumber} fehlen`);
			}

			return {
				sectionNumber,
				initialAnimalsCount: sectionData.initialAnimalsCount ?? 0,
				initialWeightGrams: sectionData.initialWeightGrams ?? 0,
				bedding: formData.installationBedding,
				parentFlocks: sectionData.parentFlocks.map((entry) => ({
					herdIdentifier: entry.herdIdentifier,
					productionWeek: entry.productionWeek ?? 0,
				})),
			};
		});

		await apiService.stallkarte.runCommand("replace-installation-details", {
			stallkarteId: stallkarte.id,
			sectionDetails,
		});

		await refetch();
		router.replace(`/stallkarte/${stallkarte.id}/check/rearing`);
	};

	useEffect(() => {
		if (holding === null) {
			router.push("/overview");
		} else if (holding) {
			setFormData((prev) => ({
				...prev,
				hatchery: holding.hatchery,
				breed: holding.breed,
			}));
		}
	}, [holding, router]);

	if (isLoading || !holding) {
		return <GenericLoaderPlaceholder />;
	}

	const validationErrors = getValidationErrors();

	const farms = holding.farms.filter((f) => f.sections.length > 0); // Disable farms without sections

	return (
		<SubPageLayout title="Neue Stallkarte" backLink={"/stallkarten"}>
			<BasicForm submitText={"Weiter"} isDisabled={!isFormValid()} onSubmit={onSubmit}>
				{/* Farmen Section */}
				<PageSection title="Farmen">
					<Select
						label="Aufzuchtfarm"
						value={formData.rearingFarm}
						onChange={(value) => updateField("rearingFarm", value)}
						options={rearingFarmOptions(farms, formData.fatteningFarm)}
						placeholder="Aufzuchtfarm auswählen"
						required={true}
					/>
					<Select
						label="Mastfarm (optional)"
						value={formData.fatteningFarm}
						onChange={(value) => updateField("fatteningFarm", value)}
						options={fatteningFarmOptions(farms, formData.rearingFarm)}
						allowClear={true}
						placeholder="Mastfarm auswählen"
					/>
					<InfoBanner type={"info"} icon={"auto"}>
						Aufzucht- und Mastfarm müssen die gleiche Anzahl an Abteilen haben. Die Filterung der
						Farmen erfolgt automatisch basierend auf der Auswahl der jeweils anderen Farm.
					</InfoBanner>
				</PageSection>

				{/* Stammdate Section */}
				<PageSection title="Stammdaten">
					<Input
						type={"date"}
						options={{
							max: todayUTC(),
						}}
						label={"Einstallungsdatum"}
						value={formData.dateStarted}
						onChange={(value) => updateField("dateStarted", value)}
						required={true}
					/>
					<div className="flex flex-col sm:flex-row space-y-6 sm:space-y-0 sm:space-x-4">
						<div className="flex-1 flex flex-col justify-end">
							<Input
								type="date"
								options={{
									max: todayUTC(),
								}}
								label="Schlupfdatum"
								value={formData.dateHatched}
								onChange={(value) => updateField("dateHatched", value)}
								required={true}
							/>
						</div>
					</div>

					<Input
						type="text"
						label="Brüterei (übernommen)"
						value={formData.hatchery}
						onChange={(value) => updateField("hatchery", value)}
						placeholder="Name der Brüterei"
						required={true}
					/>

					<div className="flex flex-col sm:flex-row space-y-6 sm:space-y-0 sm:space-x-4">
						<div className="w-full sm:w-1/3">
							<Input
								type="text"
								label="Rasse (übernommen)"
								value={formData.breed}
								onChange={(value) => updateField("breed", value)}
								placeholder="z.B. ABC-DEF"
								required={true}
							/>
						</div>
						<div className="flex-1 flex flex-col justify-end">
							<Input
								type="text"
								label="Mastdurchgang"
								value={formData.fatteningCycle}
								onChange={(value) => updateField("fatteningCycle", value)}
								placeholder="z.B. 1"
								required={true}
							/>
						</div>
					</div>

					<Input
						type="text"
						label="Öko-Kontrollnummer"
						value={holding.ecoControlNumber}
						onChange={() => {}}
						disabled={true}
						description={
							"Die Öko-Kontrollnummer wird aus den betrieblichen Angaben übernommen und kann hier nicht geändert werden."
						}
					/>

					{/* Betrieb Toggles */}
					<div className="flex flex-col">
						<span className="text-base font-medium text-on-secondary-container mb-2">Betrieb</span>
						<div className="flex flex-col space-y-3 pl-8">
							<ToggleSwitch
								label="EU-Bio"
								checked={formData.euOrganic}
								onChange={(value) => updateField("euOrganic", value)}
							/>
							<ToggleSwitch
								label="Naturland"
								checked={formData.naturland}
								onChange={(value) => updateField("naturland", value)}
							/>
						</div>
					</div>

					<Input
						type="text"
						label="Einstreu"
						value={formData.installationBedding}
						onChange={(value) => updateField("installationBedding", value)}
						placeholder="z.B. Dinkelspeizen"
						required={true}
					/>
				</PageSection>

				{selectedSections.length > 0 && (
					<PageSection title="Einstallung pro Abteil">
						<div className="space-y-6">
							{selectedSections.map((section, index) => {
								const sectionNumber = index + 1;
								const sectionData = formData.installationBySectionNumber[sectionNumber] ?? {
									initialAnimalsCount: null,
									initialWeightGrams: null,
									parentFlocks: [
										{
											id: createParentFlockId(),
											herdIdentifier: "",
											productionWeek: null,
										},
									],
								};

								return (
									<div key={section.id} className="rounded-xl bg-primary-container/20 p-4">
										<div className="mb-3 text-lg font-semibold text-primary">
											Abteil {sectionNumber}
										</div>
										<div className="mb-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
											<Input
												type="number"
												options={{ min: 1 }}
												label="Tieranzahl"
												value={sectionData.initialAnimalsCount}
												onChange={(value) =>
													updateInstallationSection(sectionNumber, {
														...sectionData,
														initialAnimalsCount: value,
													})
												}
												required={true}
											/>
											<Input
												type="number"
												options={{ min: 1 }}
												label="Gewicht"
												value={sectionData.initialWeightGrams}
												onChange={(value) =>
													updateInstallationSection(sectionNumber, {
														...sectionData,
														initialWeightGrams: value,
													})
												}
												required={true}
											/>
										</div>
										<div className="mt-6 space-y-6">
											{sectionData.parentFlocks.map((parentFlock, parentFlockIndex) => (
												<div key={parentFlock.id} className="space-y-2">
													<div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
														<Input
															type="text"
															label="Elterntier Herde"
															value={parentFlock.herdIdentifier}
															onChange={(value) => {
																const nextParentFlocks = [...sectionData.parentFlocks];
																nextParentFlocks[parentFlockIndex] = {
																	...nextParentFlocks[parentFlockIndex],
																	herdIdentifier: value,
																};
																updateInstallationSection(sectionNumber, {
																	...sectionData,
																	parentFlocks: nextParentFlocks,
																});
															}}
															placeholder="z.B. ET-1"
															required={true}
														/>
														<Input
															type="number"
															options={{ min: 1 }}
															label="Produktionswoche (PW)"
															value={parentFlock.productionWeek}
															onChange={(value) => {
																const nextParentFlocks = [...sectionData.parentFlocks];
																nextParentFlocks[parentFlockIndex] = {
																	...nextParentFlocks[parentFlockIndex],
																	productionWeek: value,
																};
																updateInstallationSection(sectionNumber, {
																	...sectionData,
																	parentFlocks: nextParentFlocks,
																});
															}}
															placeholder="z.B. 30"
															required={true}
														/>
													</div>
													{sectionData.parentFlocks.length > 1 && (
														<button
															type="button"
															onClick={() =>
																updateInstallationSection(sectionNumber, {
																	...sectionData,
																	parentFlocks: sectionData.parentFlocks.filter(
																		(entry) => entry.id !== parentFlock.id,
																	),
																})
															}
															className="text-sm font-medium text-primary"
														>
															ET/PW entfernen
														</button>
													)}
												</div>
											))}
											<button
												type="button"
												onClick={() =>
													updateInstallationSection(sectionNumber, {
														...sectionData,
														parentFlocks: [
															...sectionData.parentFlocks,
															{
																id: createParentFlockId(),
																herdIdentifier: "",
																productionWeek: null,
															},
														],
													})
												}
												className="mt-1 text-base font-medium text-primary"
											>
												+ ET/PW
											</button>
										</div>
									</div>
								);
							})}
						</div>
					</PageSection>
				)}

				{validationErrors.length > 0 && (
					<div className="mt-4 rounded-md border border-error bg-error-container p-4 text-on-error-container">
						<p className="mb-2 font-semibold">Bitte prüfen Sie folgende Pflichtfelder:</p>
						<ul className="list-disc space-y-1 pl-5 text-sm">
							{validationErrors.map((error) => (
								<li key={error}>{error}</li>
							))}
						</ul>
					</div>
				)}
			</BasicForm>
		</SubPageLayout>
	);
}
