import type React from "react";
import { GiGrain } from "react-icons/gi";
import { LuWeight } from "react-icons/lu";
import { MdOutlineWaterDrop, MdThermostat, MdWarning, MdWaves } from "react-icons/md";
import { StyledLabel } from "@/components/styled-label";
import type { StallkarteStateDay } from "@/services/domain/stallkarte";

interface EventProps {
	event: StallkarteStateDay;
	incomplete?: boolean;
}

function KpiItem({
	icon,
	value,
	unit,
}: {
	icon: React.ReactNode;
	value: string | number | null;
	unit?: string;
}) {
	return (
		<div className="flex flex-row items-center gap-1 mb-2">
			{icon}
			<div className="font-medium">
				{value ?? "???"} {unit}
			</div>
		</div>
	);
}

export default function Event({ event, incomplete }: EventProps) {
	const cycleTypes = {
		rearing: {
			label: "Aufzucht",
			type: "primary",
		},
		fattening: {
			label: "Mast",
			type: "tertiary",
		},
	} as const;

	const cycle = cycleTypes[event.productionCycle];

	return (
		<div className={`text-on-surface bg-surface py-2 px-4 rounded-lg shadow-md w-full`}>
			<h1 className="text-xl font-medium mb-2 text-primary flex items-center gap-4">
				Tag {event.productionDay}
				<StyledLabel type={cycle.type}>{cycle.label}</StyledLabel>
				{incomplete && (
					<StyledLabel type={"warning"} className={"ml-auto"} icon={<MdWarning />}>
						Unvollständig
					</StyledLabel>
				)}
			</h1>
			<div className="flex flex-row flex-wrap justify-between gap-x-2">
				<KpiItem icon={<LuWeight />} value={event.weightGrams} unit={"g"} />
				<KpiItem icon={<MdThermostat />} value={event.temperatureCelsius} unit={"°C"} />
				<KpiItem icon={<MdOutlineWaterDrop />} value={event.humidityPercent} unit={"%"} />
				<KpiItem icon={<MdWaves />} value={event.waterConsumptionLiters} unit={"L"} />
				<KpiItem icon={<GiGrain />} value={event.feedConsumptionKg} unit={"kg"} />
			</div>
		</div>
	);
}
