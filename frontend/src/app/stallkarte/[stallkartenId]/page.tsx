"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import type React from "react";
import { MdAdd, MdChecklist, MdEdit, MdEventNote, MdFileCopy, MdSync } from "react-icons/md";
import Event from "@/app/stallkarte/[stallkartenId]/event";
import { MilestoneBanner } from "@/app/stallkarte/[stallkartenId]/milestone-banner";
import Button from "@/components/button";
import GenericLoaderPlaceholder from "@/components/generic-loader-placeholder";
import PageSection from "@/components/page-section";
import SubPageLayout from "@/components/sub-page-layout";
import { useModal } from "@/contexts/ModalContext";
import { useShallowStallkarten } from "@/contexts/ShallowStallkartenContext";
import { useStallkarte } from "@/contexts/StallkarteContext";
import { apiService } from "@/services/api";
import { getMilestoneForProductionDay } from "@/services/domain/milestones";
import {
	getProductionDayOfDate,
	getTodaysProductionDay,
	isStallkarteDayFinished,
	type Stallkarte,
} from "@/services/domain/stallkarte";

const dateFormatter = new Intl.DateTimeFormat("de-DE", {
	year: "numeric",
	month: "2-digit",
	day: "2-digit",
});

function Divider({ children }: { children: React.ReactNode }) {
	return (
		<div className={"flex flex-row items-center gap-2 my-3"}>
			<div className={"h-0.5 flex-1 bg-secondary/70 rounded-full"}></div>
			<span className="text-sm text-secondary font-medium">{children}</span>
			<div className={"h-0.5 flex-1 bg-secondary/70 rounded-full"}></div>
		</div>
	);
}

interface DayProps {
	stallkarte: Stallkarte;
	productionDay: number;
}

function Day({ stallkarte, productionDay }: DayProps) {
	const content = () => {
		const existingDay = stallkarte.state.days[productionDay];
		if (!existingDay) {
			if (stallkarte.state.isFinished) {
				return (
					<div
						className={
							"flex flex-row items-center justify-center gap-2 text-primary font-medium border border-primary px-4 py-6 rounded-lg " +
							"bg-surface/50 opacity-50 cursor-not-allowed"
						}
					>
						<MdAdd size={"1.5em"} /> Tag {productionDay} protokollieren
					</div>
				);
			}
			return (
				<Link href={`/stallkarte/${stallkarte.id}/day/${productionDay}`}>
					<div
						className={
							"flex flex-row items-center justify-center gap-2 text-primary font-medium border border-primary px-4 py-6 rounded-lg " +
							"bg-surface/50"
						}
					>
						<MdAdd size={"1.5em"} /> Tag {productionDay} protokollieren
					</div>
				</Link>
			);
		}

		const isCompleted = isStallkarteDayFinished(stallkarte, productionDay);

		// TODO: Add Day overview on click? And/or direct button to edit day?
		return (
			<Link href={`/stallkarte/${stallkarte.id}/day/${productionDay}`}>
				<Event event={existingDay} incomplete={!isCompleted} />
			</Link>
		);
	};
	const isTransferDay = productionDay === stallkarte.state.transfer?.productionDay;
	const isFirstDay = productionDay === 0;
	const isFinishDay =
		stallkarte.state.dateFinished &&
		productionDay === getProductionDayOfDate(stallkarte.state, stallkarte.state.dateFinished);

	return (
		<>
			{isFinishDay && stallkarte.state.dateFinished && (
				<Divider>Abgeschlossen {dateFormatter.format(stallkarte.state.dateFinished)}</Divider>
			)}
			{content()}
			{isTransferDay && stallkarte.state.transfer && (
				<div>
					<div className={"mt-3"}>
						<Button
							type={"secondary"}
							iconLeft={<MdChecklist />}
							loaderOnClick={true}
							href={`/stallkarte/${stallkarte.id}/check/fattening`}
						>
							Serviceperiode Mast
						</Button>
					</div>
					<Divider>
						<Button
							iconRight={<MdEdit />}
							type={"link"}
							href={`/stallkarte/${stallkarte.id}/transfer/revise`}
							loaderOnClick={true}
							loaderPosition={"right"}
						>
							Umstallung {dateFormatter.format(stallkarte.state.transfer.date)}
						</Button>
					</Divider>
				</div>
			)}
			{isFirstDay && (
				<div className={"mt-3"}>
					<Button
						type={"secondary"}
						iconLeft={<MdChecklist />}
						loaderOnClick={true}
						href={`/stallkarte/${stallkarte.id}/check/rearing`}
					>
						Serviceperiode Aufzucht
					</Button>
					<Divider>Einstallung {dateFormatter.format(stallkarte.state.dateStarted)}</Divider>
				</div>
			)}
		</>
	);
}

export default function Page() {
	const { stallkarte, isLoading, refetch } = useStallkarte();
	const { showModal, hideModal } = useModal();
	const { refetch: refetchStallkarten } = useShallowStallkarten();
	const router = useRouter();

	if (isLoading || !stallkarte) {
		return (
			<SubPageLayout title={"Stallkarte"}>
				<GenericLoaderPlaceholder text={"Lade Stallkarte"} />
			</SubPageLayout>
		);
	}

	const productionDay = getTodaysProductionDay(stallkarte.state);
	const productionDaysPassed = productionDay + 1; // +1 because productionDay starts at 0
	const productionDays = Array.from({ length: productionDaysPassed }, (_, i) => i).toReversed(); // [productionDay, ..., 2, 1, 0]
	const isTransferred = !!stallkarte.state.transfer;

	const subtitleDate = dateFormatter.format(stallkarte.state.dateStarted);
	const milestone = getMilestoneForProductionDay(productionDay);

	const onDelete = () => {
		showModal({
			title: "Stallkarte löschen",
			body: (
				<p>
					Möchten Sie die abgeschlossene Stallkarte
					<span className="font-semibold"> {stallkarte.state.fatteningCycle} </span>
					wirklich löschen?
				</p>
			),
			footer: (
				<div className="flex justify-end space-x-2">
					<Button type="secondary" onClick={() => hideModal()}>
						Abbrechen
					</Button>
					<Button
						type="danger"
						onClick={async () => {
							await apiService.stallkarte.runCommand("delete-stallkarte", {
								stallkarteId: stallkarte.id,
							});
							await refetchStallkarten();
							hideModal();
							router.push("/stallkarten");
						}}
						loaderOnClick={true}
						clickBehavior={"single-click"}
					>
						Löschen
					</Button>
				</div>
			),
		});
	};

	const onReopen = () => {
		showModal({
			title: "Reaktivieren",
			body: (
				<p>
					Möchten Sie die abgeschlossene Stallkarte
					<span className="font-semibold"> {stallkarte.state.fatteningCycle} </span>
					wirklich wieder aktivieren?
				</p>
			),
			footer: (
				<div className="flex justify-end space-x-2">
					<Button type="secondary" onClick={() => hideModal()}>
						Abbrechen
					</Button>
					<Button
						type="primary"
						onClick={async () => {
							await apiService.stallkarte.runCommand("reopen-stallkarte", {
								stallkarteId: stallkarte.id,
							});
							await refetchStallkarten();
							await refetch();
							hideModal();
						}}
						loaderOnClick={true}
						clickBehavior={"single-click"}
					>
						Reaktivieren
					</Button>
				</div>
			),
		});
	};

	return (
		<SubPageLayout
			actionRight={
				stallkarte.state.isFinished ? (
					<div className="flex items-center gap-3">
						<Button type={"link"} onClick={onReopen} width={"auto"}>
							Reaktivieren
						</Button>
						<Button type={"danger-link"} onClick={onDelete} width={"auto"}>
							Löschen
						</Button>
					</div>
				) : (
					<Button type={"danger-link"} href={`/stallkarte/${stallkarte.id}/finish`} width={"auto"}>
						Schlachtung
					</Button>
				)
			}
			title={
				<div className="flex flex-row items-center justify-between gap-4">
					Stallkarte {stallkarte.state.fatteningCycle}
					{stallkarte.state.isFinished ? " – Abgeschlossen" : ""}
				</div>
			}
			subtitle={`Gestartet am ${subtitleDate} – Tag ${productionDay}`}
			backLink={`/stallkarten`}
		>
			{milestone && <MilestoneBanner milestone={milestone} />}
			<div className="flex flex-row flex-wrap items-center gap-4">
				<div className={"flex-none"}>
					<Button
						type={"secondary"}
						href={`/stallkarte/${stallkarte.id}/details`}
						iconLeft={<MdEdit />}
						width={"auto"}
						loaderOnClick={true}
					>
						Details
					</Button>
				</div>

				<div className={"grow"}>
					<Button
						type={"secondary"}
						href={`/stallkarte/${stallkarte.id}/export`}
						iconLeft={<MdFileCopy />}
						loaderOnClick={true}
						width={"auto"}
					>
						Export
					</Button>
				</div>

				{!isTransferred && (
					<div className={"grow"}>
						<Button
							type={"primary"}
							iconLeft={<MdSync />}
							href={`/stallkarte/${stallkarte.id}/transfer`}
							loaderOnClick={true}
							width={"auto"}
						>
							Umstallen
						</Button>
					</div>
				)}
			</div>
			<PageSection title={"Events"} titleIcon={<MdEventNote />} noBodyStyle={true}>
				<div className="space-y-2">
					{productionDays.map((day) => (
						<div key={day}>
							<Day stallkarte={stallkarte} productionDay={day} />
						</div>
					))}
				</div>
			</PageSection>
		</SubPageLayout>
	);
}
