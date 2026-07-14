"use client";

import { MdAdd, MdWarning } from "react-icons/md";
import GeneralNoteCard from "@/app/stallkarte/[stallkartenId]/day/[productionDay]/general-note-card";
import Button from "@/components/button";
import Input from "@/components/input";
import MultiSelect, { type MultiSelectOption } from "@/components/multi-select";
import PageSection from "@/components/page-section";
import { StyledLabel } from "@/components/styled-label";
import ToggleSwitch from "@/components/toggle-switch";
import {
	type GeneralNoteEntry,
	type GeneralNoteType,
	isSockTestNoteType,
	isTreatmentNoteType,
	isVaccinationNoteType,
	TREATMENT_AMOUNT_UNITS,
	TREATMENT_CODES,
	VACCINATION_CODES,
	WAITING_TIME_UNITS,
	WEATHER_CONDITIONS,
	type WeatherCondition,
} from "@/services/domain/stallkarte";

const weatherConditionLabels: Record<WeatherCondition, string> = {
	sun: "Sonne",
	cloudy: "Bewölkt",
	precipitation: "Niederschlag",
	extreme_wetness: "Extreme Nässe",
	frost: "Frost",
	strong_wind: "Starker Wind",
};

const weatherConditionOptions: MultiSelectOption<WeatherCondition>[] = WEATHER_CONDITIONS.map(
	(weatherCondition) => ({
		value: weatherCondition,
		label: weatherConditionLabels[weatherCondition],
	}),
);

const createNoteId = (): string => {
	if (typeof crypto !== "undefined" && crypto.randomUUID) {
		return crypto.randomUUID();
	}
	return `note-${Date.now()}-${Math.random().toString(16).slice(2)}`;
};

const createDefaultNoteEntry = (): GeneralNoteEntry => ({
	id: createNoteId(),
	isDirty: true,
	noteType: "other",
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

export interface GeneralFormData {
	temperatureCelsius: number | null;
	humidityPercent: number | null;
	weightGrams: number | null;
	feedConsumptionKg: number | null;
	waterConsumptionLiters: number | null;
	openingTime: string | null;
	weatherConditions: WeatherCondition[];
	veterinarian: boolean;
	notes: GeneralNoteEntry[];
}

interface GeneralViewProps {
	value: GeneralFormData;
	showFatteningSection: boolean;
	onChange: (value: GeneralFormData) => void;
	disabled?: boolean;
}

export default function GeneralView({
	value,
	showFatteningSection,
	onChange,
	disabled = false,
}: GeneralViewProps) {
	const formData = value;

	const updateField = <K extends keyof GeneralFormData>(field: K, value: GeneralFormData[K]) => {
		onChange({ ...formData, [field]: value });
	};

	const updateNoteAt = (index: number, next: GeneralNoteEntry) => {
		const notes = [...formData.notes];
		notes[index] = { ...next, isDirty: true };
		onChange({ ...formData, notes });
	};

	const updateNoteTypeAt = (index: number, type: GeneralNoteType) => {
		const current = formData.notes[index];
		const base: GeneralNoteEntry = {
			...current,
			noteType: type,
			deliveryReceiptNumber: null,
			batchNumber: null,
			vaccinationCode: null,
			treatmentCode: null,
			treatmentAmountValue: null,
			treatmentAmountUnit: null,
			treatmentWaitingTimeValue: null,
			treatmentWaitingTimeUnit: null,
			sockTestResult: null,
		};

		if (isVaccinationNoteType(type)) {
			base.vaccinationCode = current.vaccinationCode ?? VACCINATION_CODES[0];
		}
		if (isTreatmentNoteType(type)) {
			base.treatmentCode = current.treatmentCode ?? TREATMENT_CODES[0];
			base.treatmentAmountUnit = current.treatmentAmountUnit ?? TREATMENT_AMOUNT_UNITS[0];
			base.treatmentWaitingTimeUnit = current.treatmentWaitingTimeUnit ?? WAITING_TIME_UNITS[0];
		}
		if (isSockTestNoteType(type)) {
			base.sockTestResult = current.sockTestResult ?? "negative";
		}

		updateNoteAt(index, base);
	};

	const addNote = () => {
		onChange({
			...formData,
			notes: [...formData.notes, createDefaultNoteEntry()],
		});
	};

	const removeNote = (id: string) => {
		onChange({
			...formData,
			notes: formData.notes.filter((note) => note.id !== id),
		});
	};

	const isClimateComplete =
		formData.temperatureCelsius !== null && formData.humidityPercent !== null;
	const isFeedWaterComplete =
		formData.weightGrams !== null &&
		formData.feedConsumptionKg !== null &&
		formData.waterConsumptionLiters !== null;

	return (
		<div className="space-y-6">
			<PageSection
				title={
					<div className={"flex flex-row items-center gap-2 w-full"}>
						Klima
						{!isClimateComplete && (
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
							label="Temperatur (°C)"
							value={formData.temperatureCelsius}
							onChange={(v) => updateField("temperatureCelsius", v)}
							placeholder="z.B. 22.5"
							disabled={disabled}
						/>
					</div>
					<div className="flex-1">
						<Input
							type="number"
							label="Luftfeuchtigkeit (%)"
							value={formData.humidityPercent}
							onChange={(v) => updateField("humidityPercent", v)}
							placeholder="z.B. 1"
							disabled={disabled}
						/>
					</div>
				</div>
			</PageSection>

			<PageSection
				title={
					<div className={"flex flex-row items-center gap-2 w-full"}>
						Futter & Wasser
						{!isFeedWaterComplete && (
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
							label="Wasser (Liter)"
							value={formData.waterConsumptionLiters}
							onChange={(v) => updateField("waterConsumptionLiters", v)}
							placeholder="z.B. 22.5"
							disabled={disabled}
						/>
					</div>
					<div className="flex-1">
						<Input
							type="number"
							label="Futter (kg)"
							value={formData.feedConsumptionKg}
							onChange={(v) => updateField("feedConsumptionKg", v)}
							placeholder="z.B. 1"
							disabled={disabled}
						/>
					</div>
				</div>
				<Input
					type="number"
					label="Gewicht (g)"
					value={formData.weightGrams}
					onChange={(v) => updateField("weightGrams", v)}
					placeholder="z.B. 548"
					disabled={disabled}
				/>
			</PageSection>

			{showFatteningSection && (
				<PageSection title={"Auslauf"}>
					<div className="space-y-4">
						<Input
							type="time"
							label="Öffnungszeit"
							value={formData.openingTime}
							onChange={(v) => updateField("openingTime", v)}
							placeholder="z.B. 08:00"
							disabled={disabled}
						/>

						<MultiSelect
							label="Witterung"
							values={formData.weatherConditions}
							onChange={(v) => updateField("weatherConditions", v)}
							options={weatherConditionOptions}
							disabled={disabled}
						/>

						<ToggleSwitch
							label="Veterinaer"
							checked={formData.veterinarian}
							onChange={(v) => updateField("veterinarian", v)}
							disabled={disabled}
						/>
					</div>
				</PageSection>
			)}

			<PageSection title={"Anmerkungen"} noBodyStyle={true}>
				<div className="mt-1 space-y-2">
					{formData.notes.map((note, index) => (
						<GeneralNoteCard
							key={note.id}
							note={note}
							onRemove={removeNote}
							onUpdate={(next) => updateNoteAt(index, next)}
							onTypeChange={(type) => updateNoteTypeAt(index, type)}
							disabled={disabled}
						/>
					))}

					<Button
						type="primary"
						iconLeft={<MdAdd size={"1.5em"} />}
						onClick={addNote}
						disabled={disabled}
					>
						Notiz hinzufügen
					</Button>
				</div>
			</PageSection>
		</div>
	);
}
