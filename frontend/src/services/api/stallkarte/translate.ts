import type {
	ResponseShallowStallkarte,
	ResponseStallkarte,
	ResponseStallkarteAlarmTest,
	ResponseStallkarteChecklist,
	ResponseStallkarteFarm,
	ResponseStallkarteFinishNote,
	ResponseStallkarteLightingProgram,
	ResponseStallkartePestControlMeasures,
	ResponseStallkarteSiloCleaned,
	ResponseStallkarteStableDisinfected,
	ResponseStallkarteState,
	ResponseStallkarteStateDay,
	ResponseStallkarteStateDayNote,
	ResponseStallkarteStateDaySection,
	ResponseStallkarteTransfer,
	ResponseStallkarteWaterLineDisinfected,
} from "@/services/api/stallkarte/responses";
import type {
	FinishNoteEntry,
	GeneralNoteEntry,
	ParentFlockEntry,
	SectionInstallationDetails,
	ShallowStallkarte,
	Stallkarte,
	StallkarteAlarmTest,
	StallkarteChecklist,
	StallkarteFarm,
	StallkarteLightingProgram,
	StallkartePestControlMeasures,
	StallkarteSiloCleaned,
	StallkarteStableDisinfected,
	StallkarteState,
	StallkarteStateDay,
	StallkarteStateDaySection,
	StallkarteTransfer,
	StallkarteWaterLineDisinfected,
} from "@/services/domain/stallkarte";

const ifNotNull = <T, R>(value: T | null | undefined, transform: (value: T) => R): R | null => {
	if (value === null || value === undefined) {
		return null;
	}
	return transform(value);
};

const responseStallkarteStateDaySectionToDomain = (
	day: ResponseStallkarteStateDaySection,
): StallkarteStateDaySection => {
	return {
		sectionNumber: day.section_number,
		naturalMortalityMorning: day.natural_mortality_morning,
		naturalMortalityEvening: day.natural_mortality_evening,
		selectiveMortalityMorning: day.selective_mortality_morning,
		selectiveMortalityEvening: day.selective_mortality_evening,
		didInspectionMorning: day.did_inspection_morning,
		didInspectionEvening: day.did_inspection_evening,
		note: day.note,
	};
};

const responseStallkarteStateDayNoteToDomain = (
	note: ResponseStallkarteStateDayNote,
): GeneralNoteEntry => {
	if (note.note_type === "slaughter" || note.note_type === "catching") {
		throw new Error(`invalid day note type: ${note.note_type}`);
	}

	return {
		id: note.id,
		noteType: note.note_type,
		noteText: note.note_text,
		deliveryReceiptNumber: note.delivery_receipt_number,
		batchNumber: note.batch_number,
		vaccinationCode: note.vaccination_code,
		treatmentCode: note.treatment_code,
		treatmentAmountValue: note.treatment_amount_value,
		treatmentAmountUnit: note.treatment_amount_unit,
		treatmentWaitingTimeValue: note.treatment_waiting_time_value,
		treatmentWaitingTimeUnit: note.treatment_waiting_time_unit,
		sockTestResult: note.sock_test_result,
		slaughterDate: note.slaughter_date ? new Date(note.slaughter_date) : null,
		slaughterAnimalsCount: note.slaughter_animals_count,
		slaughterFinalWeightKg: note.slaughter_final_weight_kg,
		slaughtererName: note.slaughterer_name,
		catchingTime: note.catching_time,
		catcherName: note.catcher_name,
	};
};

const responseStallkarteFinishNoteToDomain = (
	note: ResponseStallkarteFinishNote,
): FinishNoteEntry => {
	if (note.note_type !== "slaughter" && note.note_type !== "catching") {
		throw new Error(`invalid finish note type: ${note.note_type}`);
	}

	return {
		id: note.id,
		noteType: note.note_type,
		noteText: note.note_text,
		deliveryReceiptNumber: note.delivery_receipt_number,
		batchNumber: note.batch_number,
		vaccinationCode: note.vaccination_code,
		treatmentCode: note.treatment_code,
		treatmentAmountValue: note.treatment_amount_value,
		treatmentAmountUnit: note.treatment_amount_unit,
		treatmentWaitingTimeValue: note.treatment_waiting_time_value,
		treatmentWaitingTimeUnit: note.treatment_waiting_time_unit,
		sockTestResult: note.sock_test_result,
		slaughterDate: note.slaughter_date ? new Date(note.slaughter_date) : null,
		slaughterAnimalsCount: note.slaughter_animals_count,
		slaughterFinalWeightKg: note.slaughter_final_weight_kg,
		slaughtererName: note.slaughterer_name,
		catchingTime: note.catching_time,
		catcherName: note.catcher_name,
	};
};

const responseStallkarteFarmToDomain = (farm: ResponseStallkarteFarm): StallkarteFarm => {
	return {
		id: farm.id,
		name: farm.name,
		type: farm.type,
		vvvoNumber: farm.vvvo_number,
		sections: farm.sections.map((section) => ({
			id: section.id,
			number: section.number,
			name: section.name,
		})),
	};
};

const responseStallkarteAlarmTestToDomain = (
	alarmTest: ResponseStallkarteAlarmTest,
): StallkarteAlarmTest => {
	return {
		didEmergencyPowerTest: alarmTest.did_emergency_power_test,
		didAlarmTest: alarmTest.did_alarm_test,
	};
};

const responseStallkarteLightingProgramToDomain = (
	lightingProgram: ResponseStallkarteLightingProgram,
): StallkarteLightingProgram => {
	return {
		didDarkPeriodTest: lightingProgram.did_dark_period_test,
		hadDivergenceDueToVet: lightingProgram.had_divergence_due_to_vet,
	};
};

const responseStallkartePestControlMeasuresToDomain = (
	pestControlMeasures: ResponseStallkartePestControlMeasures,
): StallkartePestControlMeasures => {
	return {
		didPerformPestControl: pestControlMeasures.did_perform_pest_control,
		annotation: pestControlMeasures.annotation,
	};
};

const responseStallkarteSiloCleanedToDomain = (
	siloCleaned: ResponseStallkarteSiloCleaned,
): StallkarteSiloCleaned => {
	return {
		date: siloCleaned.date ? new Date(siloCleaned.date) : null,
		detergent: siloCleaned.detergent,
		dosis: siloCleaned.dosis,
	};
};

const responseStallkarteStableDisinfectedToDomain = (
	stableDisinfected: ResponseStallkarteStableDisinfected,
): StallkarteStableDisinfected => {
	return {
		date: stableDisinfected.date ? new Date(stableDisinfected.date) : null,
		disinfectant: stableDisinfected.disinfectant,
		dosis: stableDisinfected.dosis,
	};
};

const responseStallkarteWaterLineDisinfectedToDomain = (
	waterLineDisinfected: ResponseStallkarteWaterLineDisinfected,
): StallkarteWaterLineDisinfected => {
	return {
		date: waterLineDisinfected.date ? new Date(waterLineDisinfected.date) : null,
		disinfectant: waterLineDisinfected.disinfectant,
		dosis: waterLineDisinfected.dosis,
	};
};

const responseStallkarteChecklistToDomain = (
	checklist: ResponseStallkarteChecklist,
): StallkarteChecklist => {
	return {
		alarmTest: ifNotNull(checklist.alarm_test, responseStallkarteAlarmTestToDomain),
		lightingProgram: ifNotNull(
			checklist.lighting_program,
			responseStallkarteLightingProgramToDomain,
		),
		pestControlMeasures: ifNotNull(
			checklist.pest_control_measures,
			responseStallkartePestControlMeasuresToDomain,
		),
		siloCleaned: ifNotNull(checklist.silo_cleaned, responseStallkarteSiloCleanedToDomain),
		stableDisinfection: ifNotNull(
			checklist.stable_disinfected,
			responseStallkarteStableDisinfectedToDomain,
		),
		waterLineDisinfected: ifNotNull(
			checklist.water_line_disinfected,
			responseStallkarteWaterLineDisinfectedToDomain,
		),
	};
};

const responseStallkarteStateDayToDomain = (
	day: ResponseStallkarteStateDay,
): StallkarteStateDay => {
	return {
		productionDay: day.production_day,
		productionCycle: day.production_cycle,
		temperatureCelsius: day.temperature_celsius,
		humidityPercent: day.humidity_percent,
		weightGrams: day.weight_grams,
		feedConsumptionKg: day.feed_consumption_kg,
		waterConsumptionLiters: day.water_consumption_liters,
		openingTime: day.opening_time,
		weatherConditions: day.weather_conditions,
		veterinarian: day.veterinarian,
		notes: day.notes.map(responseStallkarteStateDayNoteToDomain),
		sections: Object.fromEntries(
			Object.entries(day.sections).map(([sectionNumber, section]) => [
				Number(sectionNumber),
				responseStallkarteStateDaySectionToDomain(section),
			]),
		),
	};
};

const responseStallkarteTransferToDomain = (
	transfer: ResponseStallkarteTransfer,
): StallkarteTransfer => {
	const animalsBySectionNumber: Record<number, number> = {};
	for (const [sectionNumber, numberOfAnimals] of Object.entries(
		transfer.animals_by_section_number,
	)) {
		animalsBySectionNumber[Number(sectionNumber)] = numberOfAnimals;
	}
	return {
		date: new Date(transfer.date),
		productionDay: transfer.production_day,
		animalsBySectionNumber: animalsBySectionNumber,
	};
};

const responseParentFlockEntryToDomain = (
	entry: ResponseStallkarteState["installation_details_by_section"][number]["parent_flocks"][number],
): ParentFlockEntry => {
	return {
		herdIdentifier: entry.herd_identifier,
		productionWeek: entry.production_week,
	};
};

const responseSectionInstallationDetailsToDomain = (
	details: ResponseStallkarteState["installation_details_by_section"][number],
): SectionInstallationDetails => {
	return {
		sectionNumber: details.section_number,
		initialAnimalsCount: details.initial_animals_count,
		initialWeightGrams: details.initial_weight_grams,
		bedding: details.bedding,
		parentFlocks: details.parent_flocks.map(responseParentFlockEntryToDomain),
	};
};

const responseStallkarteStateToDomain = (state: ResponseStallkarteState): StallkarteState => {
	return {
		fatteningFarm: ifNotNull(state.fattening_farm, responseStallkarteFarmToDomain),
		rearingFarm: ifNotNull(state.rearing_farm, responseStallkarteFarmToDomain),
		fatteningCycle: state.fattening_cycle,
		dateStarted: new Date(state.date_started),
		dateHatched: state.date_hatched ? new Date(state.date_hatched) : null,
		hatchery: state.hatchery,
		breed: state.breed,
		ecoControlNumber: state.eco_control_number,
		transfer: ifNotNull(state.transfer, responseStallkarteTransferToDomain),
		finishNotes: state.finish_notes.map(responseStallkarteFinishNoteToDomain),
		currentCycle: state.current_cycle,
		isFinished: state.is_finished,
		dateFinished: state.date_finished ? new Date(state.date_finished) : null,
		isEuBio: state.is_eu_bio,
		isNaturland: state.is_naturland,
		installationDetailsBySection: Object.fromEntries(
			Object.entries(state.installation_details_by_section).map(([sectionNumber, details]) => [
				Number(sectionNumber),
				responseSectionInstallationDetailsToDomain(details),
			]),
		),
		days: Object.fromEntries(
			Object.entries(state.days).map(([productionDay, day]) => [
				Number(productionDay),
				responseStallkarteStateDayToDomain(day),
			]),
		),
		fatteningChecklist: ifNotNull(state.fattening_checklist, responseStallkarteChecklistToDomain),
		rearingChecklist: ifNotNull(state.rearing_checklist, responseStallkarteChecklistToDomain),
	};
};

const responseStallkarteToDomain = (response: ResponseStallkarte): Stallkarte => {
	return {
		id: response.id,
		holdingId: response.holding_id,
		state: responseStallkarteStateToDomain(response.state),
	};
};

const responseShallowStallkarteToDomain = (
	response: ResponseShallowStallkarte,
): ShallowStallkarte => {
	return {
		id: response.id,
		holdingId: response.holding_id,
		dateStarted: new Date(response.date_started),
		dateHatched: new Date(response.date_hatched),
		hatcheryName: response.hatchery_name,
		breed: response.breed,
		fatteningCycle: response.fattening_cycle,
		ecoControlNumber: response.eco_control_number,
		isEuBio: response.is_eu_bio,
		isNaturland: response.is_naturland,
		isFinished: response.is_finished,
		dateFinished: response.date_finished ? new Date(response.date_finished) : null,
	};
};

export {
	responseShallowStallkarteToDomain,
	responseStallkarteFarmToDomain,
	responseStallkarteStateDayToDomain,
	responseStallkarteStateToDomain,
	responseStallkarteToDomain,
	responseStallkarteTransferToDomain,
};
