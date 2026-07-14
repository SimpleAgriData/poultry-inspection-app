import type { RequestBody } from "@/services/api/client";
import type { StallkarteCommand, StallkarteCommands } from "@/services/api/stallkarte/commands";
import { dateUtil } from "@/services/util/date-util";

type CommandPath<T extends StallkarteCommand> = `/api/v1/stallkarte/${T}`;

type RequestBodyMapping = {
	[T in keyof StallkarteCommands]: (args: StallkarteCommands[T]) => RequestBody<CommandPath<T>>;
};

const requestBodyMapping: RequestBodyMapping = {
	"assign-fattening-farm": (args) => ({
		stallkarte_id: args.stallkarteId,
		farm_id: args.farmId,
	}),
	"assign-rearing-farm": (args) => ({
		stallkarte_id: args.stallkarteId,
		farm_id: args.farmId,
	}),
	"delete-stallkarte": (args) => ({
		stallkarte_id: args.stallkarteId,
	}),
	"finish-stallkarte": (args) => ({
		stallkarte_id: args.stallkarteId,
		date_finished: dateUtil.strDate(args.dateFinished),
		finish_notes: args.finishNotes.map((note) => ({
			id: note.id,
			note_type: note.noteType,
			slaughter_date: dateUtil.optionalStrDate(note.slaughterDate),
			slaughter_animals_count: note.slaughterAnimalsCount,
			slaughter_final_weight_kg: note.slaughterFinalWeightKg,
			slaughterer_name: note.slaughtererName,
			catching_time: note.catchingTime,
			catcher_name: note.catcherName,
		})),
	}),
	"save-finish-notes": (args) => ({
		stallkarte_id: args.stallkarteId,
		finish_notes: args.finishNotes.map((note) => ({
			id: note.id,
			note_type: note.noteType,
			slaughter_date: dateUtil.optionalStrDate(note.slaughterDate),
			slaughter_animals_count: note.slaughterAnimalsCount,
			slaughter_final_weight_kg: note.slaughterFinalWeightKg,
			slaughterer_name: note.slaughtererName,
			catching_time: note.catchingTime,
			catcher_name: note.catcherName,
		})),
	}),
	"save-general-notes": (args) => ({
		stallkarte_id: args.stallkarteId,
		production_day: args.productionDay,
		general_notes: args.generalNotes.map((note) => ({
			id: note.id,
			note_type: note.noteType,
			note_text: note.noteText,
			delivery_receipt_number: note.deliveryReceiptNumber,
			batch_number: note.batchNumber,
			vaccination_code: note.vaccinationCode,
			treatment_code: note.treatmentCode,
			treatment_amount_value: note.treatmentAmountValue,
			treatment_amount_unit: note.treatmentAmountUnit,
			treatment_waiting_time_value: note.treatmentWaitingTimeValue,
			treatment_waiting_time_unit: note.treatmentWaitingTimeUnit,
			sock_test_result: note.sockTestResult,
			slaughter_animals_count: note.slaughterAnimalsCount,
		})),
	}),
	"log-section-note": (args) => ({
		stallkarte_id: args.stallkarteId,
		production_day: args.productionDay,
		section_number: args.sectionNumber,
		note: args.note,
	}),
	"record-ambient-climate": (args) => ({
		stallkarte_id: args.stallkarteId,
		production_day: args.productionDay,
		temperature_celsius: args.temperatureCelsius,
		humidity_percent: args.humidityPercent,
	}),
	"record-feed-consumption": (args) => ({
		stallkarte_id: args.stallkarteId,
		production_day: args.productionDay,
		amount_kg: args.amountKg,
	}),
	"record-fattening-day-data": (args) => ({
		stallkarte_id: args.stallkarteId,
		production_day: args.productionDay,
		opening_time: args.openingTime,
		weather_conditions: args.weatherConditions,
		veterinarian: args.veterinarian,
	}),
	"record-mortality": (args) => ({
		stallkarte_id: args.stallkarteId,
		production_day: args.productionDay,
		section_number: args.sectionNumber,
		natural_deaths: args.naturalDeaths,
		selective_deaths: args.selectiveDeaths,
		shift: args.shift,
	}),
	"record-water-consumption": (args) => ({
		stallkarte_id: args.stallkarteId,
		production_day: args.productionDay,
		amount_liters: args.amountLiters,
	}),
	"record-weight": (args) => ({
		stallkarte_id: args.stallkarteId,
		production_day: args.productionDay,
		weight_grams: args.weightGrams,
	}),
	"reopen-stallkarte": (args) => ({
		stallkarte_id: args.stallkarteId,
	}),
	"transfer-flock": (args) => ({
		stallkarte_id: args.stallkarteId,
		transfer_date: dateUtil.strDate(args.transferDate),
		animals_by_section_number: args.animalsBySectionNumber,
	}),
	"revise-transfer-details": (args) => ({
		stallkarte_id: args.stallkarteId,
		animals_by_section_number: args.animalsBySectionNumber,
	}),
	"start-stallkarte": (args) => ({
		date_started: dateUtil.strDate(args.dateStarted),
		date_hatched: dateUtil.strDate(args.dateHatched),
		hatchery_name: args.hatcheryName,
		breed: args.breed,
		fattening_cycle: args.fatteningCycle,
		eco_control_number: args.ecoControlNumber,
		is_eu_bio: args.isEuBio,
		is_naturland: args.isNaturland,
	}),
	"replace-installation-details": (args) => ({
		stallkarte_id: args.stallkarteId,
		section_details: args.sectionDetails.map((details) => ({
			section_number: details.sectionNumber,
			initial_animals_count: details.initialAnimalsCount,
			initial_weight_grams: details.initialWeightGrams,
			bedding: details.bedding,
			parent_flocks: details.parentFlocks.map((parentFlock) => ({
				herd_identifier: parentFlock.herdIdentifier,
				production_week: parentFlock.productionWeek,
			})),
		})),
	}),
	"revise-details": (args) => ({
		stallkarte_id: args.stallkarteId,
		date_hatched: dateUtil.strDate(args.dateHatched),
		hatchery_name: args.hatcheryName,
		breed: args.breed,
		fattening_cycle: args.fatteningCycle,
		is_eu_bio: args.isEuBio,
		is_naturland: args.isNaturland,
	}),
	"perform-light-program": (args) => ({
		cycle: args.cycle,
		stallkarte_id: args.stallkarteId,
		did_dark_period_test: args.didDarkPeriodTest,
		had_divergence_due_to_vet: args.hadDivergenceDueToVet,
	}),
	"perform-alarm-test": (args) => ({
		stallkarte_id: args.stallkarteId,
		cycle: args.cycle,
		did_alarm_test: args.didAlarmTest,
		did_emergency_power_test: args.didEmergencyPowerTest,
	}),
	"apply-pest-control-measures": (args) => ({
		stallkarte_id: args.stallkarteId,
		cycle: args.cycle,
		did_perform_pest_control: args.didPerformPestControl,
		annotation: args.annotation,
	}),
	"clean-silo": (args) => ({
		stallkarte_id: args.stallkarteId,
		cycle: args.cycle,
		date: dateUtil.optionalStrDate(args.date),
		detergent: args.detergent,
		dosis: args.dosis,
	}),
	"disinfect-stable": (args) => ({
		stallkarte_id: args.stallkarteId,
		cycle: args.cycle,
		date: dateUtil.optionalStrDate(args.date),
		disinfectant: args.disinfectant,
		dosis: args.dosis,
	}),
	"disinfect-water-line": (args) => ({
		stallkarte_id: args.stallkarteId,
		cycle: args.cycle,
		date: dateUtil.optionalStrDate(args.date),
		disinfectant: args.disinfectant,
		dosis: args.dosis,
	}),
};

export type { CommandPath };
export { requestBodyMapping };
