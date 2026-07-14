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
import { useStallkarte } from "@/contexts/StallkarteContext";
import { apiService } from "@/services/api";
import { todayUTC } from "@/services/dates";
import { dateUtil } from "@/services/util/date-util";
import { coerceNull } from "@/services/util/type-util";

const ReviseStallkarteSchema = z.object({
	rearingFarm: z.number().min(1, "Aufzuchtfarm ist erforderlich"),
	fatteningFarm: z.number().nullable(),
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

interface FormData {
	rearingFarm: number | null;
	fatteningFarm: number | null;
	dateHatched: Date | null;
	hatchery: string;
	breed: string;
	fatteningCycle: string;
	euOrganic: boolean;
	naturland: boolean;
	installationBedding: string;
	installationBySectionNumber: Record<number, InstallationSectionFormData>;
}

export default function StallkarteDetailsPage() {
	const { stallkarte, refetch } = useStallkarte();
	const router = useRouter();
	const { holding } = useHolding();
	const [formData, setFormData] = useState<FormData>({
		rearingFarm: null,
		fatteningFarm: null,
		dateHatched: null,
		hatchery: "",
		breed: "",
		fatteningCycle: "",
		euOrganic: true,
		naturland: true,
		installationBedding: "",
		installationBySectionNumber: {},
	});

	useEffect(() => {
		if (stallkarte) {
			const selectedSections = stallkarte.state.rearingFarm?.sections ?? [];
			const installationBySectionNumber: Record<number, InstallationSectionFormData> = {};

			for (const section of selectedSections) {
				const sectionDetails = stallkarte.state.installationDetailsBySection[section.number];
				const parentFlocks =
					sectionDetails?.parentFlocks.map((entry) => ({
						id: createParentFlockId(),
						herdIdentifier: entry.herdIdentifier,
						productionWeek: entry.productionWeek,
					})) ?? [];
				installationBySectionNumber[section.number] = {
					initialAnimalsCount: sectionDetails?.initialAnimalsCount ?? null,
					initialWeightGrams: sectionDetails?.initialWeightGrams ?? null,
					parentFlocks:
						parentFlocks.length > 0
							? parentFlocks
							: [
									{
										id: createParentFlockId(),
										herdIdentifier: "",
										productionWeek: null,
									},
								],
				};
			}

			setFormData({
				rearingFarm: stallkarte.state.rearingFarm?.id || null,
				fatteningFarm: stallkarte.state.fatteningFarm?.id || null,
				dateHatched: stallkarte.state.dateHatched,
				hatchery: stallkarte.state.hatchery,
				breed: stallkarte.state.breed,
				fatteningCycle: stallkarte.state.fatteningCycle,
				euOrganic: stallkarte.state.isEuBio,
				naturland: stallkarte.state.isNaturland,
				installationBedding:
					selectedSections.length > 0
						? (stallkarte.state.installationDetailsBySection[selectedSections[0].number]?.bedding ??
							"")
						: "",
				installationBySectionNumber,
			});
		}
	}, [stallkarte]);

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

	const selectedSections = stallkarte?.state.rearingFarm?.sections ?? [];

	const isInstallationValid = (): boolean => {
		if (!InstallationSchema.safeParse({ bedding: formData.installationBedding }).success) {
			return false;
		}

		if (selectedSections.length === 0) {
			return false;
		}

		return selectedSections.every((section) => {
			const sectionData = formData.installationBySectionNumber[section.number];
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
			ReviseStallkarteSchema.parse(formData);
			return isInstallationValid();
		} catch (_error) {
			return false;
		}
	};

	const onSubmit = async () => {
		if (!stallkarte || !holding) return;
		try {
			const validatedData = ReviseStallkarteSchema.parse(formData);

			const didRearingFarmChange =
				validatedData.rearingFarm !== coerceNull(stallkarte.state.rearingFarm?.id);
			const didFatteningFarmChange =
				validatedData.fatteningFarm !== coerceNull(stallkarte.state.fatteningFarm?.id);
			const didDetailsChange =
				dateUtil.optionalStrDate(validatedData.dateHatched) !==
					dateUtil.optionalStrDate(stallkarte.state.dateHatched) ||
				validatedData.hatchery !== stallkarte.state.hatchery ||
				validatedData.breed !== stallkarte.state.breed ||
				validatedData.fatteningCycle !== stallkarte.state.fatteningCycle ||
				validatedData.euOrganic !== stallkarte.state.isEuBio ||
				validatedData.naturland !== stallkarte.state.isNaturland;

			const sectionDetails = selectedSections.map((section) => {
				const sectionData = formData.installationBySectionNumber[section.number];
				if (!sectionData) {
					throw new Error(`Einstallungsdaten für Abteil ${section.number} fehlen`);
				}

				return {
					sectionNumber: section.number,
					initialAnimalsCount: sectionData.initialAnimalsCount ?? 0,
					initialWeightGrams: sectionData.initialWeightGrams ?? 0,
					bedding: formData.installationBedding,
					parentFlocks: sectionData.parentFlocks.map((entry) => ({
						herdIdentifier: entry.herdIdentifier,
						productionWeek: entry.productionWeek ?? 0,
					})),
				};
			});

			const didInstallationDetailsChange = selectedSections.some((section) => {
				const sectionData = formData.installationBySectionNumber[section.number];
				if (!sectionData) {
					return true;
				}

				const currentDetails = stallkarte.state.installationDetailsBySection[section.number];
				if (!currentDetails) {
					return true;
				}

				if (
					sectionData.initialAnimalsCount !== currentDetails.initialAnimalsCount ||
					sectionData.initialWeightGrams !== currentDetails.initialWeightGrams ||
					formData.installationBedding !== currentDetails.bedding ||
					sectionData.parentFlocks.length !== currentDetails.parentFlocks.length
				) {
					return true;
				}

				return sectionData.parentFlocks.some((entry, index) => {
					const currentEntry = currentDetails.parentFlocks[index];
					if (!currentEntry) {
						return true;
					}
					return (
						entry.herdIdentifier !== currentEntry.herdIdentifier ||
						entry.productionWeek !== currentEntry.productionWeek
					);
				});
			});

			const hasChanges =
				didRearingFarmChange ||
				didFatteningFarmChange ||
				didDetailsChange ||
				didInstallationDetailsChange;

			if (!hasChanges) {
				router.back();
				return;
			}

			// Even though some combination of the following commands could be executed parallel, an error may occur if
			// the rearing and fattening farm are changed in the wrong order
			if (didDetailsChange) {
				await apiService.stallkarte.runCommand("revise-details", {
					stallkarteId: stallkarte.id,
					dateHatched: validatedData.dateHatched,
					hatcheryName: validatedData.hatchery,
					breed: validatedData.breed,
					fatteningCycle: validatedData.fatteningCycle,
					isEuBio: validatedData.euOrganic,
					isNaturland: validatedData.naturland,
				});
			}

			if (didInstallationDetailsChange) {
				await apiService.stallkarte.runCommand("replace-installation-details", {
					stallkarteId: stallkarte.id,
					sectionDetails,
				});
			}

			// The rearing farm is the required one, so we need to change this first. For example when the number of sections
			// changes, the fattening farm has to comply, not the other way around
			if (didRearingFarmChange) {
				await apiService.stallkarte.runCommand("assign-rearing-farm", {
					stallkarteId: stallkarte.id,
					farmId: validatedData.rearingFarm,
				});
			}
			if (didFatteningFarmChange && validatedData.fatteningFarm !== null) {
				await apiService.stallkarte.runCommand("assign-fattening-farm", {
					stallkarteId: stallkarte.id,
					farmId: validatedData.fatteningFarm,
				});
			}

			await refetch();
			router.back();
		} catch (error) {
			console.error("Fehler beim Speichern der Änderungen:", error);
		}
	};

	if (!stallkarte || !holding) {
		return <GenericLoaderPlaceholder text={"Lade Stallkarte"} />;
	}

	const farms = holding.farms.filter((f) => f.sections.length > 0); // Disable farms without sections
	const canAssignRearingFarm = Object.keys(stallkarte.state.days).length === 0; // Only allow assigning rearing farm if no days have been added yet
	const canAssignFatteningFarm = stallkarte.state.transfer === null; // Only allow assigning fattening farm if transfer hasn't happened yet
	const canClearFatteningFarm = stallkarte.state.fatteningFarm === null; // there is currently no way to clear an assigned farm, however not assign one at all is accepted

	return (
		<SubPageLayout title={`Stallkarte ${stallkarte.state.fatteningCycle} bearbeiten`}>
			<BasicForm
				submitText={"Speichern"}
				isDisabled={!isFormValid()}
				onSubmit={onSubmit}
				isReadOnly={stallkarte.state.isFinished}
			>
				{/* Farmen Section */}
				<PageSection title="Farmen">
					<Select
						label="Aufzuchtfarm"
						value={formData.rearingFarm}
						onChange={(value) => updateField("rearingFarm", value)}
						options={rearingFarmOptions(farms, formData.fatteningFarm)}
						placeholder="Aufzuchtfarm auswählen"
						required={true}
						disabled={!canAssignRearingFarm}
						description={
							!canAssignRearingFarm
								? "Die Aufzuchtfarm kann nur zugewiesen oder geändert werden, solange noch keine Produktionstage eingetragen wurden."
								: ""
						}
					/>
					<Select
						label="Mastfarm (optional)"
						value={formData.fatteningFarm}
						onChange={(value) => updateField("fatteningFarm", value)}
						options={fatteningFarmOptions(farms, formData.rearingFarm)}
						allowClear={canClearFatteningFarm}
						placeholder="Mastfarm auswählen"
						disabled={!canAssignFatteningFarm}
						description={
							!canAssignFatteningFarm
								? "Die Mastfarm kann nur vor der Umstallung zugewiesen oder geändert werden."
								: ""
						}
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
						value={stallkarte.state.dateStarted}
						label={"Einstallungsdatum"}
						onChange={() => {}}
						disabled={true}
						description={"Das Einstallungsdatum kann nicht geändert werden."}
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
				</PageSection>

				{selectedSections.length > 0 && (
					<PageSection title="Einstallung pro Abteil">
						<div className="space-y-6">
							<Input
								type="text"
								label="Einstreu"
								value={formData.installationBedding}
								onChange={(value) => updateField("installationBedding", value)}
								placeholder="z.B. Strohhäcksel"
								required={true}
							/>
							{selectedSections.map((section) => {
								const sectionData = formData.installationBySectionNumber[section.number] ?? {
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
											Abteil {section.number}
										</div>
										<div className="mb-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
											<Input
												type="number"
												options={{ min: 1 }}
												label="Tieranzahl"
												value={sectionData.initialAnimalsCount}
												onChange={(value) =>
													updateInstallationSection(section.number, {
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
													updateInstallationSection(section.number, {
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
																updateInstallationSection(section.number, {
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
																updateInstallationSection(section.number, {
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
																updateInstallationSection(section.number, {
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
													updateInstallationSection(section.number, {
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
			</BasicForm>
		</SubPageLayout>
	);
}
