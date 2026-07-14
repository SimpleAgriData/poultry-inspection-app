"use client";

import { useRouter } from "next/navigation";
import { use, useEffect, useState } from "react";
import FarmForm, { type FarmFormData } from "@/app/farm/farm-form";
import Button from "@/components/button";
import SubPageLayout from "@/components/sub-page-layout";
import { useHolding } from "@/contexts";
import { useModal } from "@/contexts/ModalContext";
import { apiService, type Farm } from "@/services/api";

interface EditFarmPageProps {
	params: Promise<{ farmId: string }>;
}

export default function EditFarmPage({ params }: EditFarmPageProps) {
	const { showModal, hideModal } = useModal();
	const { holding, isLoading, refetch } = useHolding();
	const { farmId: idString } = use(params);
	const id = parseInt(idString, 10);

	const [farm, setFarm] = useState<Farm | null>(null);
	const router = useRouter();

	const onSubmit = async (data: FarmFormData) => {
		await apiService.updateFarm({
			farmId: id,
			name: data.name,
			type: data.type,
			vvvoNumber: data.vvvoNumber,
		});
		await refetch();

		router.push("/overview");
	};

	useEffect(() => {
		if (holding) {
			const foundFarm = holding.farms.find((f) => f.id === id) || null;
			setFarm(foundFarm);
		} else {
			setFarm(null);
		}
	}, [holding, id]);

	const onDelete = () => {
		showModal({
			title: "Farm löschen",
			body: (
				<p>
					Möchten Sie die Farm
					<span className="font-semibold"> {farm?.name} </span>
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
							await apiService.deleteFarm(id);
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
			<SubPageLayout title="Farm bearbeiten" backLink="/overview">
				<div>Lade Farm...</div>
			</SubPageLayout>
		);
	}

	if (!farm) {
		return (
			<SubPageLayout title="Farm bearbeiten" backLink="/overview">
				<div>Farm nicht gefunden.</div>
			</SubPageLayout>
		);
	}

	return (
		<SubPageLayout
			title="Farm bearbeiten"
			backLink="/overview"
			actionRight={
				<Button type="danger-link" onClick={onDelete}>
					Löschen
				</Button>
			}
		>
			<FarmForm onSubmit={onSubmit} submitText={"Speichern"} initialData={farm}></FarmForm>
		</SubPageLayout>
	);
}
