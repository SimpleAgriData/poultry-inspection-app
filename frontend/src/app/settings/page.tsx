"use client";

import type React from "react";

import { useState } from "react";
import { MdEdit, MdLogout } from "react-icons/md";
import Button from "@/components/button";
import GenericLoaderPlaceholder from "@/components/generic-loader-placeholder";
import { PageLayout } from "@/components/page-layout";
import PageSection from "@/components/page-section";
import { useAuth, useHolding } from "@/contexts";
import { useApi } from "@/contexts/ApiContext";
import { useModal } from "@/contexts/ModalContext";
import { authService } from "@/services/auth";

function UserSection() {
	const { user } = useAuth();
	const { showModal, hideModal } = useModal();

	const handleLogout = () => {
		showModal({
			title: "Logout bestätigen",
			body: <p>Sind Sie sicher, dass Sie sich abmelden möchten?</p>,
			footer: (
				<div className="flex justify-end gap-2">
					<Button type="secondary" onClick={hideModal}>
						Abbrechen
					</Button>
					<Button
						type="danger"
						onClick={() => {
							// noinspection JSIgnoredPromiseFromCall
							authService.logout();
						}}
					>
						Abmelden
					</Button>
				</div>
			),
		});
	};

	return (
		<div className={"flex flex-col gap-4"}>
			{!user ? (
				<GenericLoaderPlaceholder height={"auto"} />
			) : (
				<>
					<div className="text-on-surface flex flex-row gap-2">
						<p className={"font-semibold "}>Angemeldet als:</p>
						<p>
							{user?.firstName} {user?.lastName}
						</p>
					</div>
					<div className={"flex justify-end"}>
						<Button
							type="danger-link"
							iconLeft={<MdLogout />}
							width={"auto"}
							onClick={handleLogout}
						>
							Logout
						</Button>
					</div>
				</>
			)}
		</div>
	);
}

function UserHoldingSection() {
	const { holding } = useHolding();

	if (!holding) {
		return (
			<div className={"flex flex-col gap-4"}>
				<GenericLoaderPlaceholder height={"auto"} />
			</div>
		);
	}

	const formattedAddress = `${holding.addressStreet}, ${holding.addressZip} ${holding.addressCity}`;

	return (
		<div className={"flex flex-col gap-4"}>
			<div className="flex justify-between">
				<span className="text-on-surface-variant">Name:</span>
				<span className="text-on-surface font-medium">{holding.name}</span>
			</div>
			<div className="flex justify-between">
				<span className="text-on-surface-variant">Adresse:</span>
				<span className="text-on-surface font-medium">{formattedAddress}</span>
			</div>
			<div className="flex justify-between">
				<span className="text-on-surface-variant">Öko-Kontrollnr.:</span>
				<span className="text-on-surface font-medium">{holding.ecoControlNumber}</span>
			</div>
			<div className="flex justify-between">
				<span className="text-on-surface-variant">Brüterei:</span>
				<span className="text-on-surface font-medium">{holding.hatchery}</span>
			</div>
			<div className="flex justify-between">
				<span className="text-on-surface-variant">Tierrasse:</span>
				<span className="text-on-surface font-medium">{holding.breed}</span>
			</div>
			<div className="flex justify-end">
				<Button
					type="link"
					href="/holding"
					width={"auto"}
					iconLeft={<MdEdit />}
					loaderOnClick={true}
				>
					Betriebsdaten bearbeiten
				</Button>
			</div>
		</div>
	);
}

interface GridItem {
	label: string;
	value?: React.ReactNode;
}

function GridRow({
	label,
	value,
	expandedRows,
}: GridItem & {
	expandedRows?: GridItem[];
}) {
	const [isExpanded, setIsExpanded] = useState(false);

	const handleClick = () => {
		if (!expandedRows) {
			return;
		}
		setIsExpanded(!isExpanded);
	};

	return (
		<>
			{expandedRows ? (
				<>
					<button
						type="button"
						className="font-medium pr-4 text-left bg-transparent border-none p-0 cursor-pointer"
						onClick={handleClick}
					>
						{label}
					</button>
					<button
						type="button"
						className="overflow-hidden whitespace-nowrap text-ellipsis text-left bg-transparent border-none p-0 cursor-pointer"
						onClick={handleClick}
					>
						{!isExpanded ? value : ""}
					</button>
				</>
			) : (
				<>
					<p className="font-medium pr-4">{label}</p>
					<span className={"overflow-hidden whitespace-nowrap text-ellipsis"}>{value}</span>
				</>
			)}

			{isExpanded &&
				expandedRows?.map((row, index) =>
					row.value ? (
						[
							<p
								key={
									/* biome-ignore lint/suspicious/noArrayIndexKey: this is a static list that won't change, so using the index as key is acceptable here */ `${index}-${row.label}-label`
								}
								className={`pl-4 ${index === expandedRows?.length - 1 ? "pb-2" : ""}`}
							>
								{row.label}
							</p>,
							<p
								key={
									/* biome-ignore lint/suspicious/noArrayIndexKey: this is a static list that won't change, so using the index as key is acceptable here */ `${index}-${row.value}-label`
								}
								className={"overflow-hidden whitespace-nowrap text-ellipsis"}
							>
								{row.value}
							</p>,
						]
					) : (
						<p
							key={
								/* biome-ignore lint/suspicious/noArrayIndexKey: this is a static list that won't change, so using the index as key is acceptable here */ `${index}-${row.label}-label-only`
							}
							className={`pl-4 ${index === expandedRows?.length - 1 ? "pb-2" : ""} ${
								!row.value ? "col-span-2" : ""
							}`}
						>
							{row.label}
						</p>
					),
				)}
		</>
	);
}

function AboutSection() {
	const { apiUrl, connectionState, lastStatus } = useApi();
	const parsedUrl = new URL(apiUrl);
	const formattedApiUrl = `${parsedUrl.host}${parsedUrl.pathname}`;

	const apiVersionFormat = lastStatus ? lastStatus.version : "N/A";
	const apiGitVersionFormat = lastStatus ? lastStatus.gitVersion : "N/A";

	const appVersion = process.env.NEXT_PUBLIC_VERSION || "N/A";
	const appGitVersion = process.env.NEXT_PUBLIC_GIT_VERSION || "N/A";

	return (
		<div className={"flex flex-col gap-4 text-on-surface-variant"}>
			<p className="text-on-surface font-semibold">SiAD Stallkarte App</p>
			<p className="text-on-surface text-sm">
				Die SiAD Stallkarte App ist eine mobile Anwendung zur Verwaltung und Anzeige von
				Stallkarten. Sie wurde im Rahmen des SimpleAgriData Projekts der Hochschule Karlsruhe
				entwickelt.
			</p>
			<div className={"grid grid-cols-2 gap-1 mb-2"}>
				<GridRow
					label={"App Version"}
					value={`${appVersion} / ${appGitVersion}`}
					expandedRows={[
						{ label: "Version", value: appVersion },
						{ label: "Git Version", value: appGitVersion },
					]}
				/>
				<hr className="col-span-2 border-outline my-2" />
				<GridRow
					label={"API URL"}
					value={formattedApiUrl}
					expandedRows={[{ label: formattedApiUrl }]}
				/>
				<GridRow
					label={"API Status"}
					value={
						connectionState === "connected"
							? "Verbunden"
							: connectionState === "connecting"
								? "Verbindung wird hergestellt..."
								: "Getrennt"
					}
				/>
				<GridRow
					label={"API Version"}
					value={`${apiVersionFormat} / ${apiGitVersionFormat}`}
					expandedRows={[
						{ label: "Version", value: apiVersionFormat },
						{ label: "Git Version", value: apiGitVersionFormat },
					]}
				/>
			</div>
		</div>
	);
}

export default function SettingsPage() {
	return (
		<PageLayout className={"space-y-4"}>
			<h1 className="text-4xl font-bold text-on-surface mb-4 w-full">Einstellungen</h1>
			<PageSection title="Benutzer">
				<UserSection />
			</PageSection>
			<PageSection title="Betrieb">
				<UserHoldingSection />
			</PageSection>
			<PageSection title="Über">
				<AboutSection />
			</PageSection>
		</PageLayout>
	);
}
