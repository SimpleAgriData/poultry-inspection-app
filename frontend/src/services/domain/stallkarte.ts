import { getDaysDiff, todayUTC } from "@/services/dates";
import type { FarmType } from "@/services/domain/holding";
import { allNonNull } from "@/services/util/array-util";

interface StallkarteStateDaySection {
	sectionNumber: number;
	naturalMortalityMorning: number | null;
	naturalMortalityEvening: number | null;
	selectiveMortalityMorning: number | null;
	selectiveMortalityEvening: number | null;
	didInspectionMorning: boolean;
	didInspectionEvening: boolean;
	note: string | null;
}

type SectionNumber = number;

interface StallkarteSection {
	id: number;
	number: SectionNumber; // section number independent of the id. To use for identifying sections in the stallkarte state across rearing/fattening farms.
	name: string;
}

interface StallkarteFarm {
	id: number;
	name: string;
	type: FarmType;
	vvvoNumber: string;
	sections: StallkarteSection[];
}

type StallkarteCycle = "rearing" | "fattening";

const NOTE_TYPES = [
	"vaccination",
	"treatment",
	"feeding",
	"relocation",
	"sock_test",
	"other",
	"slaughter",
	"catching",
] as const;
const GENERAL_NOTE_TYPES = [
	"vaccination",
	"treatment",
	"feeding",
	"relocation",
	"sock_test",
	"other",
] as const;
const FINISH_NOTE_TYPES = ["slaughter", "catching"] as const;

const VACCINATION_CODES = ["nd", "gumboro", "ib"] as const;
const TREATMENT_CODES = [
	"amproline",
	"pyanosid",
	"lincospectin",
	"phenoxypen_wsp",
	"baytril",
	"lanflox",
] as const;
const TREATMENT_AMOUNT_UNITS = ["l/1000", "g/1000", "ml", "mg", "l", "kg"] as const;
const WAITING_TIME_UNITS = ["day", "week"] as const;
const SOCK_TEST_RESULTS = ["positive", "negative"] as const;
const WEATHER_CONDITIONS = [
	"sun",
	"cloudy",
	"precipitation",
	"extreme_wetness",
	"frost",
	"strong_wind",
] as const;

type NoteType = (typeof NOTE_TYPES)[number];
type GeneralNoteType = (typeof GENERAL_NOTE_TYPES)[number];
type FinishNoteType = (typeof FINISH_NOTE_TYPES)[number];
type VaccinationCode = (typeof VACCINATION_CODES)[number];
type TreatmentCode = (typeof TREATMENT_CODES)[number];
type TreatmentAmountUnit = (typeof TREATMENT_AMOUNT_UNITS)[number];
type WaitingTimeUnit = (typeof WAITING_TIME_UNITS)[number];
type SockTestResult = (typeof SOCK_TEST_RESULTS)[number];
type WeatherCondition = (typeof WEATHER_CONDITIONS)[number];

interface GeneralNoteEntry {
	id: string;
	isDirty?: boolean;
	noteType: GeneralNoteType;
	noteText: string | null;
	deliveryReceiptNumber: string | null;
	batchNumber: string | null;
	vaccinationCode: VaccinationCode | null;
	treatmentCode: TreatmentCode | null;
	treatmentAmountValue: number | null;
	treatmentAmountUnit: TreatmentAmountUnit | null;
	treatmentWaitingTimeValue: number | null;
	treatmentWaitingTimeUnit: WaitingTimeUnit | null;
	sockTestResult: SockTestResult | null;
	slaughterDate: Date | null;
	slaughterAnimalsCount: number | null;
	slaughterFinalWeightKg: number | null;
	slaughtererName: string | null;
	catchingTime: string | null;
	catcherName: string | null;
}

interface FinishNoteEntry {
	id: string;
	noteType: FinishNoteType;
	noteText: string | null;
	deliveryReceiptNumber: string | null;
	batchNumber: string | null;
	vaccinationCode: VaccinationCode | null;
	treatmentCode: TreatmentCode | null;
	treatmentAmountValue: number | null;
	treatmentAmountUnit: TreatmentAmountUnit | null;
	treatmentWaitingTimeValue: number | null;
	treatmentWaitingTimeUnit: WaitingTimeUnit | null;
	sockTestResult: SockTestResult | null;
	slaughterDate: Date | null;
	slaughterAnimalsCount: number | null;
	slaughterFinalWeightKg: number | null;
	slaughtererName: string | null;
	catchingTime: string | null;
	catcherName: string | null;
}

interface StallkarteStateDay {
	productionDay: number;
	productionCycle: StallkarteCycle;
	temperatureCelsius: number | null;
	humidityPercent: number | null;
	weightGrams: number | null;
	feedConsumptionKg: number | null;
	waterConsumptionLiters: number | null;
	openingTime: string | null;
	weatherConditions: WeatherCondition[];
	veterinarian: boolean;
	sections: Record<SectionNumber, StallkarteStateDaySection>;
	notes: GeneralNoteEntry[];
}

interface StallkarteTransfer {
	date: Date;
	productionDay: number;
	animalsBySectionNumber: Record<SectionNumber, number>;
}

interface ParentFlockEntry {
	herdIdentifier: string;
	productionWeek: number;
}

interface SectionInstallationDetails {
	sectionNumber: number;
	initialAnimalsCount: number;
	initialWeightGrams: number;
	bedding: string;
	parentFlocks: ParentFlockEntry[];
}

interface StallkarteAlarmTest {
	didEmergencyPowerTest: boolean | null;
	didAlarmTest: boolean | null;
}

interface StallkarteLightingProgram {
	didDarkPeriodTest: boolean | null;
	hadDivergenceDueToVet: boolean | null;
}

interface StallkartePestControlMeasures {
	didPerformPestControl: boolean | null;
	annotation: string | null;
}

interface StallkarteSiloCleaned {
	date: Date | null;
	detergent: string | null;
	dosis: string | null;
}

interface StallkarteStableDisinfected {
	date: Date | null;
	disinfectant: string | null;
	dosis: string | null;
}

interface StallkarteWaterLineDisinfected {
	date: Date | null;
	disinfectant: string | null;
	dosis: string | null;
}

interface StallkarteChecklist {
	alarmTest: StallkarteAlarmTest | null;
	lightingProgram: StallkarteLightingProgram | null;
	pestControlMeasures: StallkartePestControlMeasures | null;
	siloCleaned: StallkarteSiloCleaned | null;
	stableDisinfection: StallkarteStableDisinfected | null;
	waterLineDisinfected: StallkarteWaterLineDisinfected | null;
}

interface StallkarteState {
	fatteningFarm: StallkarteFarm | null;
	rearingFarm: StallkarteFarm | null;
	fatteningCycle: string;
	dateStarted: Date;
	dateHatched: Date | null;
	transfer: StallkarteTransfer | null;
	hatchery: string;
	breed: string;
	ecoControlNumber: string;
	currentCycle: StallkarteCycle;
	isFinished: boolean;
	dateFinished: Date | null;
	finishNotes: FinishNoteEntry[];
	isEuBio: boolean;
	isNaturland: boolean;
	installationDetailsBySection: Record<SectionNumber, SectionInstallationDetails>;

	rearingChecklist: StallkarteChecklist | null;
	fatteningChecklist: StallkarteChecklist | null;

	days: Record<number, StallkarteStateDay>;
}

interface Stallkarte {
	id: number;
	holdingId: number;
	state: StallkarteState;
}

interface ShallowStallkarte {
	id: number;
	holdingId: number;
	dateStarted: Date;
	dateHatched: Date;
	hatcheryName: string;
	breed: string;
	fatteningCycle: string;
	ecoControlNumber: string;
	isEuBio: boolean;
	isNaturland: boolean;
	isFinished: boolean;
	dateFinished: Date | null;
}

const getStallkarteFarmOfDay = (
	stallkarte: Stallkarte,
	productionDay: number,
): StallkarteFarm | null => {
	const transferDay = stallkarte.state.transfer?.productionDay ?? null;
	if (transferDay === null) {
		return stallkarte.state.rearingFarm;
	}

	if (productionDay < transferDay) {
		return stallkarte.state.rearingFarm;
	} else {
		return stallkarte.state.fatteningFarm;
	}
};

const getProductionDayOfDate = (
	state: Pick<StallkarteState, "dateStarted" | "dateFinished">,
	date: Date,
): number => {
	if (state.dateFinished && date > state.dateFinished) {
		return getDaysDiff(state.dateStarted, state.dateFinished);
	} else {
		return getDaysDiff(state.dateStarted, date);
	}
};

const getTodaysProductionDay = (
	state: Pick<StallkarteState, "dateStarted" | "dateFinished">,
): number => {
	return getProductionDayOfDate(state, todayUTC());
};

const getDateOfProductionDay = (
	state: Pick<StallkarteState, "dateStarted">,
	productionDay: number,
): Date => {
	const resultDate = new Date(state.dateStarted);
	resultDate.setDate(state.dateStarted.getDate() + productionDay);
	return resultDate;
};

const getStallkarteChecklist = (
	state: Pick<StallkarteState, "fatteningChecklist" | "rearingChecklist">,
	cycle: StallkarteCycle,
): StallkarteChecklist | null => {
	switch (cycle) {
		case "fattening":
			return state.fatteningChecklist;
		case "rearing":
			return state.rearingChecklist;
	}
};

const isStallkarteDayFinished = (stallkarte: Stallkarte, productionDay: number): boolean => {
	const stallkarteDay: StallkarteStateDay | undefined = stallkarte.state.days[productionDay];
	if (!stallkarteDay) {
		return false;
	}
	const farm = getStallkarteFarmOfDay(stallkarte, productionDay);
	if (!farm) {
		// Probably no assigned fattening farm after transfer
		return false;
	}

	const hasGeneralData = allNonNull([
		stallkarteDay.weightGrams,
		stallkarteDay.temperatureCelsius,
		stallkarteDay.humidityPercent,
		stallkarteDay.waterConsumptionLiters,
		stallkarteDay.feedConsumptionKg,
	]);

	const isSectionCompleted = (section: StallkarteStateDaySection) => {
		return allNonNull([
			section.naturalMortalityEvening,
			section.selectiveMortalityEvening,
			section.naturalMortalityMorning,
			section.selectiveMortalityMorning,
		]);
	};

	const hasAllSectionData = farm.sections.every((s) => {
		const sectionData: StallkarteStateDaySection | undefined = stallkarteDay.sections[s.number];
		return sectionData ? isSectionCompleted(sectionData) : false;
	});

	return hasGeneralData && hasAllSectionData;
};

const isVaccinationNoteType = (noteType: NoteType | null): boolean => {
	return noteType === "vaccination";
};

const isTreatmentNoteType = (noteType: NoteType | null): boolean => {
	return noteType === "treatment";
};

const isSockTestNoteType = (noteType: NoteType | null): boolean => {
	return noteType === "sock_test";
};

const isSlaughterFinishNoteType = (noteType: FinishNoteType | null): boolean => {
	return noteType === "slaughter";
};

const isCatchingFinishNoteType = (noteType: FinishNoteType | null): boolean => {
	return noteType === "catching";
};

export type {
	FinishNoteEntry,
	FinishNoteType,
	GeneralNoteEntry,
	GeneralNoteType,
	NoteType,
	ParentFlockEntry,
	SectionInstallationDetails,
	SectionNumber,
	ShallowStallkarte,
	SockTestResult,
	Stallkarte,
	StallkarteAlarmTest,
	StallkarteChecklist,
	StallkarteCycle,
	StallkarteFarm,
	StallkarteLightingProgram,
	StallkartePestControlMeasures,
	StallkarteSection,
	StallkarteSiloCleaned,
	StallkarteStableDisinfected,
	StallkarteState,
	StallkarteStateDay,
	StallkarteStateDaySection,
	StallkarteTransfer,
	StallkarteWaterLineDisinfected,
	TreatmentAmountUnit,
	TreatmentCode,
	VaccinationCode,
	WaitingTimeUnit,
	WeatherCondition,
};

export {
	FINISH_NOTE_TYPES,
	GENERAL_NOTE_TYPES,
	getDateOfProductionDay,
	getProductionDayOfDate,
	getStallkarteChecklist,
	getStallkarteFarmOfDay,
	getTodaysProductionDay,
	isCatchingFinishNoteType,
	isSlaughterFinishNoteType,
	isSockTestNoteType,
	isStallkarteDayFinished,
	isTreatmentNoteType,
	isVaccinationNoteType,
	NOTE_TYPES,
	SOCK_TEST_RESULTS,
	TREATMENT_AMOUNT_UNITS,
	TREATMENT_CODES,
	VACCINATION_CODES,
	WAITING_TIME_UNITS,
	WEATHER_CONDITIONS,
};
