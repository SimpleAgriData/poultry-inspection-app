"use client";

import { useRouter } from "next/navigation";
import { use, useEffect, useState } from "react";
import SectionForm, { type SectionFormData } from "@/app/farm/[farmId]/section/section-form";
import Button from "@/components/button";
import SubPageLayout from "@/components/sub-page-layout";
import { useHolding } from "@/contexts";
import { useModal } from "@/contexts/ModalContext";
import { apiService, type Farm, type Section } from "@/services/api";
import { getSections } from "@/services/domain/holding";

interface EditBarnPageProps {
	params: Promise<{ sectionId: string; farmId: string }>;
}

interface Context {
	farm: Farm;
	section: Section;
}

export default function EditBarnPage({ params }: EditBarnPageProps) {
	const { showModal, hideModal } = useModal();
	const { holding, refetch, isLoading } = useHolding();
	const { farmId: farmIdString, sectionId: sectionIdString } = use(params);
	const sectionId = parseInt(sectionIdString, 10);
	const farmId = parseInt(farmIdString, 10);

	const [ctx, setCtx] = useState<Context | null>(null);
	const router = useRouter();

	const onSubmit = async (data: SectionFormData) => {
		await apiService.updateSection({
			sectionId: sectionId,
			name: data.name,
		});
		await refetch();

		router.push("/overview");
	};

	useEffect(() => {
		if (holding) {
			const foundSection = getSections(holding).find((f) => f.id === sectionId) || null;
			const foundFarm = holding.farms.find((f) => f.id === farmId);
			if (foundSection && foundFarm) {
				setCtx({ section: foundSection, farm: foundFarm });
			} else {
				router.push("/");
			}
		} else {
			setCtx(null);
		}
	}, [holding, sectionId, farmId, router]);

	const onDelete = () => {
		const displayName = `#${ctx?.section.name} (${ctx?.farm.name})`;
		showModal({
			title: "Abteil löschen",
			body: (
				<p>
					Möchten Sie das Abteil
					<span className="font-semibold"> {displayName} </span>
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
							await apiService.deleteSection(sectionId);
							await refetch();
							hideModal();
							router.push("/overview");
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
			<SubPageLayout title="Abteil bearbeiten" backLink="/overview">
				<div>Lade Abteil...</div>
			</SubPageLayout>
		);
	}

	if (!ctx) {
		return (
			<SubPageLayout title="Abteil bearbeiten" backLink="/overview">
				<div>Abteil nicht gefunden.</div>
			</SubPageLayout>
		);
	}

	const { section, farm } = ctx;

	return (
		<SubPageLayout
			title="Abteil bearbeiten"
			backLink="/overview"
			actionRight={
				<Button type="danger-link" onClick={onDelete}>
					Löschen
				</Button>
			}
		>
			<SectionForm
				onSubmit={onSubmit}
				submitText={"Speichern"}
				farm={farm}
				initialData={{
					name: section.name,
				}}
			></SectionForm>
		</SubPageLayout>
	);
}
