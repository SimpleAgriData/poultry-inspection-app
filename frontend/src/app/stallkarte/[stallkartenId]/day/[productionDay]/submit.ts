import type { GeneralFormData } from "@/app/stallkarte/[stallkartenId]/day/[productionDay]/general-view";
import type { SectionFormData } from "@/app/stallkarte/[stallkartenId]/day/[productionDay]/section-view";
import { apiService } from "@/services/api";
import type { StallkarteCommand, StallkarteCommands } from "@/services/api/stallkarte/commands";
import type {
	GeneralNoteEntry,
	Stallkarte,
	StallkarteStateDay,
	WeatherCondition,
} from "@/services/domain/stallkarte";

export interface DayFormData {
	general: GeneralFormData;
	sections: Record<number, SectionFormData>;
}

type ContextLessRequestArgs<K extends StallkarteCommand> = Omit<
	StallkarteCommands[K],
	"stallkarteId" | "productionDay"
>;

type Command<K extends StallkarteCommand> = {
	command: K;
	data: ContextLessRequestArgs<K>;
};

const getClimateDataCommand = (
	existing: StallkarteStateDay | undefined,
	temperatureCelsius: number | null,
	humidityPercent: number | null,
): Command<"record-ambient-climate"> | null => {
	const existingTemp = existing?.temperatureCelsius ?? null;
	const existingHumidity = existing?.humidityPercent ?? null;

	const didTemperatureChange = existingTemp !== temperatureCelsius;
	const didHumidityChange = existingHumidity !== humidityPercent;

	const didClimateChange = didTemperatureChange || didHumidityChange;

	if (didClimateChange) {
		return {
			command: "record-ambient-climate",
			data: {
				humidityPercent: humidityPercent,
				temperatureCelsius: temperatureCelsius,
			},
		};
	}
	return null;
};

const getWaterConsumptionCommand = (
	existing: StallkarteStateDay | undefined,
	waterConsumptionLiters: number,
): Command<"record-water-consumption"> | null => {
	const existingWaterConsumption = existing?.waterConsumptionLiters ?? null;

	const hasExistingData = existingWaterConsumption !== null;
	const didWaterConsumptionChange = existingWaterConsumption !== waterConsumptionLiters;

	if (!hasExistingData || didWaterConsumptionChange) {
		return {
			command: "record-water-consumption",
			data: {
				amountLiters: waterConsumptionLiters,
			},
		};
	}
	return null;
};

const getFeedConsumptionCommand = (
	existing: StallkarteStateDay | undefined,
	feedConsumptionKg: number,
): Command<"record-feed-consumption"> | null => {
	const existingFeedConsumption = existing?.feedConsumptionKg ?? null;

	const hasExistingData = existingFeedConsumption !== null;
	const didFeedConsumptionChange = existingFeedConsumption !== feedConsumptionKg;

	if (!hasExistingData || didFeedConsumptionChange) {
		return {
			command: "record-feed-consumption",
			data: {
				amountKg: feedConsumptionKg,
			},
		};
	}
	return null;
};

const getWeightCommand = (
	existing: StallkarteStateDay | undefined,
	weightGrams: number,
): Command<"record-weight"> | null => {
	const existingWeight = existing?.weightGrams ?? null;

	const hasExistingData = existingWeight !== null;
	const didWeightChange = existingWeight !== weightGrams;

	if (!hasExistingData || didWeightChange) {
		return {
			command: "record-weight",
			data: {
				weightGrams: weightGrams,
			},
		};
	}
	return null;
};

const areWeatherConditionsEqual = (a: WeatherCondition[], b: WeatherCondition[]): boolean => {
	if (a.length !== b.length) {
		return false;
	}

	for (let i = 0; i < a.length; i += 1) {
		if (a[i] !== b[i]) {
			return false;
		}
	}

	return true;
};

const getFatteningDayDataCommand = (
	stallkarte: Stallkarte,
	productionDay: number,
	existing: StallkarteStateDay | undefined,
	openingTime: string | null,
	weatherConditions: WeatherCondition[],
	veterinarian: boolean,
): Command<"record-fattening-day-data"> | null => {
	const transferDay = stallkarte.state.transfer?.productionDay ?? null;
	if (transferDay === null || productionDay < transferDay) {
		return null;
	}

	const existingOpeningTime = existing?.openingTime ?? null;
	const existingWeatherConditions = existing?.weatherConditions ?? [];
	const existingVeterinarian = existing?.veterinarian ?? false;

	const didOpeningTimeChange = existingOpeningTime !== openingTime;
	const didWeatherConditionsChange = !areWeatherConditionsEqual(
		existingWeatherConditions,
		weatherConditions,
	);
	const didVeterinarianChange = existingVeterinarian !== veterinarian;

	if (!didOpeningTimeChange && !didWeatherConditionsChange && !didVeterinarianChange) {
		return null;
	}

	return {
		command: "record-fattening-day-data",
		data: {
			openingTime,
			weatherConditions,
			veterinarian,
		},
	};
};

const areNoteIdsAndOrderEqual = (a: GeneralNoteEntry[], b: GeneralNoteEntry[]): boolean => {
	if (a.length !== b.length) {
		return false;
	}

	for (let i = 0; i < a.length; i += 1) {
		if (a[i].id !== b[i].id) {
			return false;
		}
	}

	return true;
};

const getSaveGeneralNotesCommand = (
	existing: StallkarteStateDay | undefined,
	notes: GeneralNoteEntry[],
): Command<"save-general-notes"> | null => {
	const existingNotes = existing?.notes ?? [];
	const didNoteStructureChange = !areNoteIdsAndOrderEqual(existingNotes, notes);
	const hasDirtyNotes = notes.some((note) => note.isDirty === true);

	if (!didNoteStructureChange && !hasDirtyNotes) {
		return null;
	}

	const cleanNotes = notes.map(({ isDirty: _isDirty, ...note }) => note);

	return {
		command: "save-general-notes",
		data: {
			generalNotes: cleanNotes,
		},
	};
};

const getMortalityCommandsForShift = (
	existing: StallkarteStateDay | undefined,
	sectionNumber: number,
	shift: "morning" | "evening",
	naturalMortality: number | null,
	selectiveMortality: number | null,
): Command<"record-mortality">[] => {
	const commands: Command<"record-mortality">[] = [];
	const existingSection = existing?.sections[sectionNumber];

	let existingNatural: number | null = null;
	let existingSelective: number | null = null;

	if (shift === "morning") {
		existingNatural = existingSection?.naturalMortalityMorning ?? null;
		existingSelective = existingSection?.selectiveMortalityMorning ?? null;
	} else if (shift === "evening") {
		existingNatural = existingSection?.naturalMortalityEvening ?? null;
		existingSelective = existingSection?.selectiveMortalityEvening ?? null;
	}

	const didNaturalChange = existingNatural !== naturalMortality;
	const didSelectiveChange = existingSelective !== selectiveMortality;

	const didMortalityChange = didNaturalChange || didSelectiveChange;

	if (didMortalityChange) {
		commands.push({
			command: "record-mortality",
			data: {
				sectionNumber: sectionNumber,
				naturalDeaths: naturalMortality,
				selectiveDeaths: selectiveMortality,
				shift: shift,
			},
		});
	}

	return commands;
};

const getMortalityCommands = (
	existing: StallkarteStateDay | undefined,
	sectionNumber: number,
	naturalMortalityMorning: number | null,
	selectiveMortalityMorning: number | null,
	naturalMortalityEvening: number | null,
	selectiveMortalityEvening: number | null,
): Command<"record-mortality">[] => {
	const commands: Command<"record-mortality">[] = [];

	if (naturalMortalityMorning !== null || selectiveMortalityMorning !== null) {
		commands.push(
			...getMortalityCommandsForShift(
				existing,
				sectionNumber,
				"morning",
				naturalMortalityMorning,
				selectiveMortalityMorning,
			),
		);
	}

	if (naturalMortalityEvening !== null || selectiveMortalityEvening !== null) {
		commands.push(
			...getMortalityCommandsForShift(
				existing,
				sectionNumber,
				"evening",
				naturalMortalityEvening,
				selectiveMortalityEvening,
			),
		);
	}

	return commands;
};

const getGeneralCommands = (
	stallkarte: Stallkarte,
	productionDay: number,
	existing: StallkarteStateDay | undefined,
	data: GeneralFormData,
): Command<StallkarteCommand>[] => {
	const commands: Command<StallkarteCommand>[] = [];

	if (data.temperatureCelsius !== null || data.humidityPercent !== null) {
		const climateCommand = getClimateDataCommand(
			existing,
			data.temperatureCelsius,
			data.humidityPercent,
		);
		if (climateCommand) {
			commands.push(climateCommand);
		}
	}

	if (data.waterConsumptionLiters !== null) {
		const waterCommand = getWaterConsumptionCommand(existing, data.waterConsumptionLiters);
		if (waterCommand) {
			commands.push(waterCommand);
		}
	}

	if (data.feedConsumptionKg !== null) {
		const feedCommand = getFeedConsumptionCommand(existing, data.feedConsumptionKg);
		if (feedCommand) {
			commands.push(feedCommand);
		}
	}

	if (data.weightGrams !== null) {
		const weightCommand = getWeightCommand(existing, data.weightGrams);
		if (weightCommand) {
			commands.push(weightCommand);
		}
	}

	const fatteningDayDataCommand = getFatteningDayDataCommand(
		stallkarte,
		productionDay,
		existing,
		data.openingTime,
		data.weatherConditions,
		data.veterinarian,
	);
	if (fatteningDayDataCommand) {
		commands.push(fatteningDayDataCommand);
	}

	const noteCommand = getSaveGeneralNotesCommand(existing, data.notes);
	if (noteCommand) {
		commands.push(noteCommand);
	}

	return commands;
};

const getSectionCommands = (
	existing: StallkarteStateDay | undefined,
	sections: Record<number, SectionFormData>,
): Command<StallkarteCommand>[] => {
	const commands: Command<StallkarteCommand>[] = [];

	for (const [sectionNumberStr, data] of Object.entries(sections)) {
		const sectionNumber = parseInt(sectionNumberStr, 10);

		const mortalityCommands = getMortalityCommands(
			existing,
			sectionNumber,
			data.naturalMortalityMorning,
			data.selectiveMortalityMorning,
			data.naturalMortalityEvening,
			data.selectiveMortalityEvening,
		);
		commands.push(...mortalityCommands);

		const existingNote = existing?.sections[sectionNumber]?.note ?? null;
		if (existingNote !== data.note) {
			commands.push({
				command: "log-section-note",
				data: {
					sectionNumber: sectionNumber,
					note: data.note ?? "",
				},
			} satisfies Command<"log-section-note">);
		}
	}

	return commands;
};

const applyCommands = async (
	stallkarteId: number,
	productionDay: number,
	commands: Command<StallkarteCommand>[],
) => {
	const requests: Promise<unknown>[] = [];
	for (const cmd of commands) {
		const requestArgs = {
			...cmd.data,
			stallkarteId: stallkarteId,
			productionDay: productionDay,
		} as StallkarteCommands[typeof cmd.command];

		const request = apiService.stallkarte.runCommand(cmd.command, requestArgs);
		requests.push(request);
	}
	await Promise.all(requests);
};

export function submitDayFormData(
	stallkarte: Stallkarte,
	productionDay: number,
	data: DayFormData,
) {
	const existing: StallkarteStateDay | undefined = stallkarte.state.days[productionDay];

	const commands: Command<StallkarteCommand>[] = [];

	const generalCommands = getGeneralCommands(stallkarte, productionDay, existing, data.general);
	commands.push(...generalCommands);

	const sectionCommands = getSectionCommands(existing, data.sections);
	commands.push(...sectionCommands);

	return applyCommands(stallkarte.id, productionDay, commands);
}
