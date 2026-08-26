import { MdDelete } from "react-icons/md";
import Button from "@/components/button";
import Input from "@/components/input";
import Select, { type SelectOption } from "@/components/select";
import TextArea from "@/components/text-area";
import ToggleSwitch from "@/components/toggle-switch";
import {
	type GeneralNoteEntry,
	type GeneralNoteType,
	isSockTestNoteType,
	isTreatmentNoteType,
	isVaccinationNoteType,
	SOCK_TEST_RESULTS,
	TREATMENT_AMOUNT_UNITS,
	TREATMENT_CODES,
	type TreatmentAmountUnit,
	type TreatmentCode,
	VACCINATION_CODES,
	type VaccinationCode,
	WAITING_TIME_UNITS,
} from "@/services/domain/stallkarte";

const noteTypeOptions: SelectOption<GeneralNoteType>[] = [
	{ value: "vaccination", label: "Impfung" },
	{ value: "treatment", label: "Behandlung" },
	{ value: "feeding", label: "Fütterung" },
	{ value: "sock_test", label: "Sockenprobe" },
	{ value: "other", label: "Sonstiges" },
];

const vaccinationCodeLabels: Record<VaccinationCode, string> = {
	nd: "ND",
	gumboro: "Gumboro",
	ib: "IB",
	kokzidien: "Kokzidien",
};

const treatmentCodeLabels: Record<TreatmentCode, string> = {
	amproline: "Amproline",
	pyanosid: "Pyanosid",
	lincospectin: "Lincospectin",
	phenoxypen_wsp: "Phenoxypen WSP",
	baytril: "Baytril",
	lanflox: "Lanflox",
	amoxicillin: "Amoxicillin",
	aviapen: "Aviapen",
	baycox: "Baycox",
	biocillin: "Biocillin",
	dozuril: "Dozuril",
	enro_sleecol: "Enro-Sleecol",
	enroxal: "Enroxal",
	neomycinsulfat: "Neomycinsulfat",
	octacillin: "Octacillin",
	parofor: "Parofor",
	pharmasin:"Pharmasin",
	rhemox_forte: "Rhemox Forte",
	solomocta: "Solomocta",
	t_s_sol: "T.S. Sol",
	toltra_k: "Toltra-K",
};

const vaccinationCodeOptions: SelectOption<VaccinationCode>[] = VACCINATION_CODES.map((code) => ({
	value: code,
	label: vaccinationCodeLabels[code],
}));

const treatmentCodeOptions: SelectOption<TreatmentCode>[] = TREATMENT_CODES.map((code) => ({
	value: code,
	label: treatmentCodeLabels[code],
}));

const treatmentAmountUnitOptions: SelectOption<TreatmentAmountUnit>[] = [
	{ value: "l/1000", label: "l/1000" },
	{ value: "g/1000", label: "g/1000" },
	{ value: "ml", label: "ml" },
	{ value: "mg", label: "mg" },
	{ value: "l", label: "l" },
	{ value: "kg", label: "kg" },
];

const waitingTimeUnitOptions: SelectOption<(typeof WAITING_TIME_UNITS)[number]>[] = [
	{ value: "day", label: "Tag" },
	{ value: "week", label: "Woche" },
];

interface GeneralNoteCardProps {
	note: GeneralNoteEntry;
	onRemove: (id: string) => void;
	onUpdate: (next: GeneralNoteEntry) => void;
	onTypeChange: (type: GeneralNoteType) => void;
	disabled?: boolean;
}

export default function GeneralNoteCard({
	note,
	onRemove,
	onUpdate,
	onTypeChange,
	disabled = false,
}: GeneralNoteCardProps) {
	return (
		<div className="w-full bg-surface-container rounded-lg shadow-md p-3 space-y-3">
			<div className="flex items-center gap-2">
				<div className="ml-auto">
					<Button
						type="link"
						width="auto"
						iconLeft={<MdDelete />}
						onClick={() => onRemove(note.id)}
						disabled={disabled}
					>
						Entfernen
					</Button>
				</div>
			</div>

			<Select
				label="Ereignistyp"
				value={note.noteType}
				onChange={(v) => onTypeChange(v as GeneralNoteType)}
				options={noteTypeOptions}
				required={true}
				disabled={disabled}
			/>

			{isVaccinationNoteType(note.noteType) && (
				<>
					<Input
						type="text"
						label="Nr. Abgabebeleg"
						value={note.deliveryReceiptNumber}
						onChange={(v) =>
							onUpdate({
								...note,
								deliveryReceiptNumber: v,
							})
						}
						disabled={disabled}
					/>
					<Input
						type="text"
						label="Chargennummer"
						value={note.batchNumber}
						onChange={(v) =>
							onUpdate({
								...note,
								batchNumber: v,
							})
						}
						disabled={disabled}
					/>
					<Select
						label="Impfcode"
						value={note.vaccinationCode}
						onChange={(v) =>
							onUpdate({
								...note,
								vaccinationCode: (v as VaccinationCode | null) ?? VACCINATION_CODES[0],
							})
						}
						options={vaccinationCodeOptions}
						required={true}
						disabled={disabled}
					/>
				</>
			)}

			{isTreatmentNoteType(note.noteType) && (
				<>
					<Input
						type="text"
						label="Nr. Abgabebeleg"
						value={note.deliveryReceiptNumber}
						onChange={(v) =>
							onUpdate({
								...note,
								deliveryReceiptNumber: v,
							})
						}
						disabled={disabled}
					/>
					<Input
						type="text"
						label="Chargennummer"
						value={note.batchNumber}
						onChange={(v) =>
							onUpdate({
								...note,
								batchNumber: v,
							})
						}
						disabled={disabled}
					/>
					<Select
						label="Behandlungscode"
						value={note.treatmentCode}
						onChange={(v) =>
							onUpdate({
								...note,
								treatmentCode: (v as TreatmentCode | null) ?? TREATMENT_CODES[0],
							})
						}
						options={treatmentCodeOptions}
						required={true}
						disabled={disabled}
					/>
					<Input
						type="number"
						label="Menge"
						value={note.treatmentAmountValue}
						onChange={(v) =>
							onUpdate({
								...note,
								treatmentAmountValue: v,
							})
						}
						disabled={disabled}
						placeholder="z.B. 1"
						required={true}
					/>
					<Select
						label="Einheit (Menge)"
						value={note.treatmentAmountUnit}
						onChange={(v) =>
							onUpdate({
								...note,
								treatmentAmountUnit: (v as TreatmentAmountUnit | null) ?? TREATMENT_AMOUNT_UNITS[0],
							})
						}
						options={treatmentAmountUnitOptions}
						required={true}
						disabled={disabled}
					/>
					<Input
						type="number"
						label="Wartezeit"
						value={note.treatmentWaitingTimeValue}
						onChange={(v) =>
							onUpdate({
								...note,
								treatmentWaitingTimeValue: v === null ? null : Math.max(0, v),
							})
						}
						disabled={disabled}
						placeholder="z.B. 0"
						required={true}
					/>
					<Select
						label="Einheit (Wartezeit)"
						value={note.treatmentWaitingTimeUnit}
						onChange={(v) =>
							onUpdate({
								...note,
								treatmentWaitingTimeUnit:
									(v as (typeof WAITING_TIME_UNITS)[number] | null) ?? WAITING_TIME_UNITS[0],
							})
						}
						options={waitingTimeUnitOptions}
						required={true}
						disabled={disabled}
					/>
				</>
			)}

			{isSockTestNoteType(note.noteType) && (
				<ToggleSwitch
					label="Ergebnis"
					checked={(note.sockTestResult ?? SOCK_TEST_RESULTS[1]) === SOCK_TEST_RESULTS[0]}
					onChange={(checked) =>
						onUpdate({
							...note,
							sockTestResult: checked ? SOCK_TEST_RESULTS[0] : SOCK_TEST_RESULTS[1],
						})
					}
					disabled={disabled}
				/>
			)}

			<TextArea
				value={note.noteText || ""}
				label={"Bemerkung"}
				onChange={(v) => onUpdate({ ...note, noteText: v })}
				placeholder={"z.B. Auffälligkeiten, besondere Vorkommnisse, etc."}
				disabled={disabled}
			/>
		</div>
	);
}
