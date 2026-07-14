"use client";

import Link from "next/link";
import { MdAdd, MdEdit } from "react-icons/md";
import Button from "@/components/button";
import GenericLoaderPlaceholder from "@/components/generic-loader-placeholder";
import { PageLayout } from "@/components/page-layout";
import PageSection from "@/components/page-section";
import { StyledLabel, type StyledLabelType } from "@/components/styled-label";
import { type Holding, useHolding } from "@/contexts";
import type { Farm, Section } from "@/services/api";

function SectionOverView({ farmId, section }: { farmId: number; section: Section }) {
	return (
		<div
			className="w-full mb-2 bg-surface-container rounded-md px-3 py-1 flex flex-row justify-between items-center
		even:bg-surface-container-highest"
		>
			<p className="font-semibold text-on-surface truncate text-nowrap">{section.name}</p>
			<Button
				type="link"
				width="auto"
				iconLeft={<MdEdit />}
				href={`/farm/${farmId}/section/${section.id}`}
				loaderOnClick={true}
			>
				Bearbeiten
			</Button>
		</div>
	);
}

function FarmOverview({ farm }: { farm: Farm }) {
	const farmTypes = {
		rearing: {
			label: "Aufzuchtfarm",
			type: "primary",
		},
		fattening: {
			label: "Mastfarm",
			type: "tertiary",
		},
		combined: {
			label: "Kombifarm",
			type: "secondary",
		},
	} satisfies Record<string, { label: string; type: StyledLabelType }>;
	return (
		<div className="w-full bg-surface-container rounded-lg shadow-md p-3 flex flex-col">
			<h2 className="text-xl font-semibold text-on-surface mb-2 flex justify-between items-center">
				{farm.name}
				<StyledLabel type={farmTypes[farm.type].type}>{farmTypes[farm.type].label}</StyledLabel>
			</h2>
			<p className="text-on-surface mb-1">
				VVVO-Nr.: <span className="font-medium">{farm.vvvoNumber}</span>
			</p>
			<div className="mb-3">
				<p className="text-on-surface font-semibold mb-1">Abteile:</p>
				{farm.sections.length === 0 ? (
					<p className="text-on-surface-variant">Keine Abteile vorhanden.</p>
				) : (
					farm.sections.map((section) => (
						<SectionOverView key={section.id} section={section} farmId={farm.id} />
					))
				)}
				<Button
					type="link"
					iconLeft={<MdAdd />}
					href={`/farm/${farm.id}/section/new`}
					loaderOnClick={true}
				>
					Abteil hinzufügen
				</Button>
			</div>
			<div className="flex justify-end">
				<Button
					type="link"
					width="auto"
					iconLeft={<MdEdit />}
					href={`/farm/${farm.id}`}
					loaderOnClick={true}
				>
					Farm Bearbeiten
				</Button>
			</div>
		</div>
	);
}

function Header({ holding }: { holding: Holding }) {
	return (
		<Link href="/holding" className="w-full">
			<h1 className="text-4xl font-bold text-on-surface mb-4 w-full flex gap-4">
				<span className="line-clamp-1">{holding.name}</span>
				<MdEdit className="shrink-0 mt-1" size="0.8em" />
			</h1>
		</Link>
	);
}

function Overview() {
	const { holding } = useHolding();

	if (holding === undefined || holding === null) {
		return <GenericLoaderPlaceholder />;
	}

	return (
		<PageLayout>
			<Header holding={holding} />
			<PageSection title={`Meine Farmen (${holding.farms.length})`} noBodyStyle={true}>
				<div className={"space-y-2"}>
					{holding.farms.map((farm) => (
						<FarmOverview key={farm.id} farm={farm} />
					))}
					{holding.farms.length === 0 && (
						<p className="text-on-surface-variant mb-4">Es wurde noch keine Farm angelegt.</p>
					)}
					<Button
						type="primary"
						iconLeft={<MdAdd size={"1.5em"} />}
						href="/farm/new"
						loaderOnClick={true}
					>
						Neue Farm hinzufügen
					</Button>
				</div>
			</PageSection>
		</PageLayout>
	);
}

export default Overview;
