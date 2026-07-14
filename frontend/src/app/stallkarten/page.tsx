"use client";

import { MdAdd, MdEdit } from "react-icons/md";
import Button from "@/components/button";
import GenericLoaderPlaceholder from "@/components/generic-loader-placeholder";
import { PageLayout } from "@/components/page-layout";
import PageSection from "@/components/page-section";
import { useModal } from "@/contexts/ModalContext";
import { useShallowStallkarten } from "@/contexts/ShallowStallkartenContext";
import { apiService } from "@/services/api";
import { getTodaysProductionDay, type ShallowStallkarte } from "@/services/domain/stallkarte";

function StallkartenOverview({
	stallkarte,
	onDelete,
}: {
	stallkarte: ShallowStallkarte;
	onDelete: (stallkarte: ShallowStallkarte) => void;
}) {
	const dateFormatter = new Intl.DateTimeFormat("de-DE", {
		year: "numeric",
		month: "2-digit",
		day: "2-digit",
	});

	return (
		<div className="w-full bg-surface-container rounded-lg shadow-md p-3 flex flex-row justify-between items-center">
			<div className="flex flex-col">
				<p className="font-semibold text-on-surface truncate text-nowrap">
					Stallkarte {stallkarte.fatteningCycle}
				</p>
				<p className="text-on-secondary-container text-sm">
					{stallkarte.isFinished && stallkarte.dateFinished
						? `Abgeschlossen am ${dateFormatter.format(stallkarte.dateFinished)}`
						: `Gestartet am ${dateFormatter.format(stallkarte.dateStarted)} – Tag ${getTodaysProductionDay(stallkarte)}`}
				</p>
			</div>

			{stallkarte.isFinished ? (
				<div className="flex items-center gap-3">
					<Button type="danger-link" width="auto" onClick={() => onDelete(stallkarte)}>
						Löschen
					</Button>
					<Button
						type="link"
						width="auto"
						href={`/stallkarte/${stallkarte.id}`}
						loaderOnClick={true}
					>
						Details
					</Button>
				</div>
			) : (
				<Button
					type="link"
					width="auto"
					iconLeft={<MdEdit />}
					href={`/stallkarte/${stallkarte.id}`}
					loaderOnClick={true}
				>
					Bearbeiten
				</Button>
			)}
		</div>
	);
}

export default function StallkartePage() {
	const { activeStallkarten, archivedStallkarten, isLoading, refetch } = useShallowStallkarten();
	const { showModal, hideModal } = useModal();

	const onDelete = (stallkarte: ShallowStallkarte) => {
		showModal({
			title: "Stallkarte löschen",
			body: (
				<p>
					Möchten Sie die abgeschlossene Stallkarte
					<span className="font-semibold"> {stallkarte.fatteningCycle} </span>
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
							await refetch();
							hideModal();
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

	if (isLoading) {
		return (
			<PageLayout>
				<GenericLoaderPlaceholder text={"Lade Stallkarten"} />
			</PageLayout>
		);
	}

	return (
		<PageLayout>
			<h1 className="text-4xl font-bold text-on-surface mb-4 w-full">Stallkarten</h1>
			<div className={"w-full flex flex-col gap-8"}>
				<PageSection title={`Meine Stallkarten (${activeStallkarten.length})`} noBodyStyle={true}>
					<div className={"mt-1 space-y-2"}>
						{activeStallkarten.map((stallkarte) => (
							<StallkartenOverview
								key={stallkarte.id}
								stallkarte={stallkarte}
								onDelete={onDelete}
							/>
						))}
						{activeStallkarten.length === 0 && (
							<p className="text-on-surface-variant mb-4">
								Es wurden noch keine Stallkarten angelegt.
							</p>
						)}
						<Button
							type="primary"
							iconLeft={<MdAdd size={"1.5em"} />}
							href="/stallkarte/new"
							loaderOnClick={true}
						>
							Neue Stallkarte erstellen
						</Button>
					</div>
				</PageSection>
				<PageSection
					title={`Abgeschlossene Stallkarten (${archivedStallkarten.length})`}
					noBodyStyle={true}
				>
					<div className={"mt-1 space-y-2"}>
						{archivedStallkarten.map((stallkarte) => (
							<StallkartenOverview
								key={stallkarte.id}
								stallkarte={stallkarte}
								onDelete={onDelete}
							/>
						))}
						{archivedStallkarten.length === 0 && (
							<p className="text-on-surface-variant mb-4">
								Es gibt noch keine abgeschlossenen Stallkarten.
							</p>
						)}
					</div>
				</PageSection>
			</div>
		</PageLayout>
	);
}
