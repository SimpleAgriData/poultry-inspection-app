"use client";

import { useEffect, useState } from "react";
import { MdFileDownload } from "react-icons/md";
import Button from "@/components/button";
import GenericLoaderPlaceholder from "@/components/generic-loader-placeholder";
import PageSection from "@/components/page-section";
import SubPageLayout from "@/components/sub-page-layout";
import { useStallkarte } from "@/contexts/StallkarteContext";
import { apiService } from "@/services/api";

export default function ExportPage() {
	const { stallkarte } = useStallkarte();
	const [exportedFile, setExportedFile] = useState<Blob | null>(null);
	const [error, setError] = useState<string | null>(null);
	const stallkarteId = stallkarte?.id;

	useEffect(() => {
		if (!stallkarteId) {
			return;
		}

		const abortController = new AbortController();

		const loadFile = async () => {
			try {
				const file = await apiService.stallkarte.exportStallkarte(
					stallkarteId,
					abortController.signal,
				);
				setExportedFile(file);
			} catch (err) {
				if (err instanceof Error) {
					if (err.name === "AbortError") {
						// Ignore abort errors
						return;
					}
					setError(`Fehler beim Laden der Datei: ${err.message}`);
					return;
				}
				setError("Fehler beim Laden der Datei. Bitte versuchen Sie es später erneut.");
				return;
			}
		};

		loadFile();

		return () => {
			abortController.abort();
		};
	}, [stallkarteId]);

	if (!stallkarte) {
		return (
			<SubPageLayout title={"Stallkarte exportieren"}>
				<GenericLoaderPlaceholder text={"Lade Stallkarte"} />
			</SubPageLayout>
		);
	}

	const downloadName = `Stallkarte_${stallkarte.state.fatteningCycle}.xlsx`;

	const handleDownload = () => {
		if (!exportedFile || !stallkarte) {
			return;
		}

		const url = URL.createObjectURL(exportedFile);
		const link = document.createElement("a");
		link.href = url;
		link.download = downloadName;
		document.body.appendChild(link);
		link.click();
		document.body.removeChild(link);
		URL.revokeObjectURL(url);
	};

	return (
		<SubPageLayout
			title={"Stallkarte exportieren"}
			subtitle={`Stallkarte ${stallkarte.state.fatteningCycle}`}
			backLink={`/stallkarte/${stallkarte.id}`}
		>
			<PageSection title={"Datei"}>
				{error && <p className={"text-error mb-4"}>{error}</p>}
				<Button
					type={"link"}
					iconLeft={<MdFileDownload />}
					withLoader={!exportedFile}
					disabled={!exportedFile}
					onClick={handleDownload}
				>
					Download {downloadName}
				</Button>
			</PageSection>
			<Button type={"secondary"} href={`/stallkarte/${stallkarte.id}`}>
				Zurück zur Stallkarte
			</Button>
		</SubPageLayout>
	);
}
