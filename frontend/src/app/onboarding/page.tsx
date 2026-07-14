"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { FaEgg } from "react-icons/fa";
import { GiChicken } from "react-icons/gi";
import { MdBusiness, MdCheck, MdInfo, MdLocationOn } from "react-icons/md";
import { z } from "zod";
import Button from "@/components/button";
import GenericLoaderPlaceholder from "@/components/generic-loader-placeholder";
import Input from "@/components/input";
import { useAuth, useHolding } from "@/contexts";
import { apiService } from "@/services/api";
import { authService } from "@/services/auth";

const OnboardingSchema = z.object({
	holdingName: z.string().min(1, "Betriebsname ist erforderlich").trim(),
	street: z.string().min(1, "Straße ist erforderlich").trim(),
	zipCode: z.string().min(1, "PLZ ist erforderlich").trim(),
	city: z.string().min(1, "Ort ist erforderlich").trim(),
	ecoControlNr: z.string().min(1, "Öko-Kontrollnummer ist erforderlich").trim(),
	hatchery: z.string().min(1, "Brüterei ist erforderlich").trim(),
	breedName: z.string().min(1, "Tierrasse ist erforderlich").trim(),
});

const StepOneSchema = OnboardingSchema.pick({ holdingName: true });
const StepTwoSchema = OnboardingSchema.pick({
	street: true,
	zipCode: true,
	city: true,
});
const StepThreeSchema = OnboardingSchema.pick({
	ecoControlNr: true,
	hatchery: true,
	breedName: true,
});

type OnboardingData = z.input<typeof OnboardingSchema>;

function Onboarding() {
	const { user } = useAuth();
	const { holding, refetch: refreshHolding } = useHolding();
	const router = useRouter();
	const [submitting, setSubmitting] = useState<boolean>(false);
	const [step, setStep] = useState<number>(1);
	const [data, setData] = useState<OnboardingData>({
		holdingName: "",
		street: "",
		zipCode: "",
		city: "",
		ecoControlNr: "",
		hatchery: "",
		breedName: "",
	});

	useEffect(() => {
		if (holding !== null && holding !== undefined) {
			router.push("/overview");
		}
	}, [holding, router]);

	const totalSteps = 4;

	const isStepValid = (): boolean => {
		try {
			switch (step) {
				case 1:
					StepOneSchema.parse({ holdingName: data.holdingName });
					return true;
				case 2:
					StepTwoSchema.parse({
						street: data.street,
						zipCode: data.zipCode,
						city: data.city,
					});
					return true;
				case 3:
					StepThreeSchema.parse({
						ecoControlNr: data.ecoControlNr,
						hatchery: data.hatchery,
						breedName: data.breedName,
					});
					return true;
				case 4:
					return true;
				default:
					return false;
			}
		} catch (_error) {
			return false;
		}
	};

	const handleNext = () => {
		if (step < totalSteps) {
			setStep(step + 1);
		}
	};

	const handleBack = () => {
		if (step > 1) {
			setStep(step - 1);
		}
	};

	const handleComplete = async () => {
		if (submitting) return;
		try {
			const validatedData = OnboardingSchema.parse(data);
			setSubmitting(true);

			await apiService.addHolding({
				name: validatedData.holdingName,
				addressStreet: validatedData.street,
				addressZip: validatedData.zipCode,
				addressCity: validatedData.city,
				ecoControlNumber: validatedData.ecoControlNr,
				hatchery: validatedData.hatchery,
				breed: validatedData.breedName,
			});
			await refreshHolding();

			router.push("/overview");
		} catch (_error) {
			console.error("Validation failed:", _error);
		}
	};

	const StepIndicator = () => (
		<div className="flex items-center justify-center space-x-2 mb-8">
			{Array.from({ length: totalSteps }, (_, i) => i + 1).map((s) => (
				<div
					key={s}
					className={`w-3 h-3 rounded-full transition-all duration-300 ${
						s === step ? "bg-primary w-8" : s < step ? "bg-primary" : "bg-outline-variant"
					}`}
				/>
			))}
		</div>
	);

	const renderStep = () => {
		switch (step) {
			case 1:
				return (
					<div className="space-y-6">
						<div className="text-center space-y-4">
							<div className="flex justify-center">
								<div className="w-16 h-16 bg-primary-container rounded-full flex items-center justify-center">
									<MdBusiness className="w-8 h-8 text-on-primary-container" />
								</div>
							</div>
							<h1 className="text-2xl font-bold text-on-surface">Ihr Betrieb</h1>
							<p className="text-on-surface-variant">Wie heißt Ihr landwirtschaftlicher Betrieb?</p>
						</div>
						<Input
							label="Betriebsname"
							placeholder="Musterhof"
							type="text"
							value={data.holdingName}
							onChange={(value) => setData({ ...data, holdingName: value })}
							iconLeft={<MdBusiness />}
							required={true}
						/>
					</div>
				);
			case 2:
				return (
					<div className="space-y-6">
						<div className="text-center space-y-4">
							<div className="flex justify-center">
								<div className="w-16 h-16 bg-primary-container rounded-full flex items-center justify-center">
									<MdLocationOn className="w-8 h-8 text-on-primary-container" />
								</div>
							</div>
							<h1 className="text-2xl font-bold text-on-surface">Standort</h1>
							<p className="text-on-surface-variant">Wo befindet sich Ihr Betrieb?</p>
						</div>
						<Input
							label="Straße und Hausnummer"
							placeholder="Musterstraße 1"
							type="text"
							value={data.street}
							onChange={(value) => setData({ ...data, street: value })}
							iconLeft={<MdLocationOn />}
							required={true}
						/>
						<div className="flex space-x-4">
							<div className="w-1/3">
								<Input
									label="PLZ"
									placeholder="12345"
									type="text"
									inputMode={"numeric"}
									value={data.zipCode}
									onChange={(value) => setData({ ...data, zipCode: value })}
									required={true}
								/>
							</div>
							<div className="flex-1">
								<Input
									label="Ort"
									placeholder="Musterstadt"
									type="text"
									value={data.city}
									onChange={(value) => setData({ ...data, city: value })}
									required={true}
								/>
							</div>
						</div>
					</div>
				);
			case 3:
				return (
					<div className="space-y-6">
						<div className="text-center space-y-4">
							<div className="flex justify-center">
								<div className="w-16 h-16 bg-primary-container rounded-full flex items-center justify-center">
									<MdInfo className="w-8 h-8 text-on-primary-container" />
								</div>
							</div>
							<h1 className="text-2xl font-bold text-on-surface">Betriebsdetails</h1>
							<p className="text-on-surface-variant">Weitere Informationen zu Ihrem Betrieb.</p>
						</div>
						<Input
							label="Öko-Kontrollnummer"
							placeholder="DE-ÖKO-000"
							type="text"
							value={data.ecoControlNr}
							onChange={(value) => setData({ ...data, ecoControlNr: value })}
							iconLeft={<MdBusiness />}
							required={true}
						/>
						<Input
							label="Brüterei"
							placeholder="Name der Brüterei"
							type="text"
							value={data.hatchery}
							onChange={(value) => setData({ ...data, hatchery: value })}
							iconLeft={<FaEgg />}
							required={true}
						/>
						<Input
							label="Tierrasse"
							placeholder="z.B. Lohmann Brown"
							type="text"
							value={data.breedName}
							onChange={(value) => setData({ ...data, breedName: value })}
							iconLeft={<GiChicken />}
							required={true}
						/>
					</div>
				);
			case 4:
				return (
					<div className="space-y-6">
						<div className="text-center space-y-4">
							<div className="flex justify-center">
								<div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center">
									<MdCheck className="w-8 h-8 text-on-primary" />
								</div>
							</div>
							<h1 className="text-2xl font-bold text-on-surface">Alles fertig!</h1>
							<p className="text-on-surface-variant">
								Ihre Daten wurden erfolgreich erfasst. Sie können jetzt loslegen.
							</p>
						</div>
						<div className="bg-surface-container rounded-lg p-4 space-y-3">
							<div className="flex justify-between">
								<span className="text-on-surface-variant">Betrieb:</span>
								<span className="text-on-surface font-medium">{data.holdingName}</span>
							</div>
							<div className="flex justify-between">
								<span className="text-on-surface-variant">Adresse:</span>
								<span className="text-on-surface font-medium text-right">
									{data.street}, {data.zipCode} {data.city}
								</span>
							</div>
							<div className="flex justify-between">
								<span className="text-on-surface-variant">Öko-Kontrollnr.:</span>
								<span className="text-on-surface font-medium">{data.ecoControlNr}</span>
							</div>
							<div className="flex justify-between">
								<span className="text-on-surface-variant">Brüterei:</span>
								<span className="text-on-surface font-medium">{data.hatchery}</span>
							</div>
							<div className="flex justify-between">
								<span className="text-on-surface-variant">Tierrasse:</span>
								<span className="text-on-surface font-medium">{data.breedName}</span>
							</div>
						</div>
					</div>
				);
			default:
				return null;
		}
	};

	if (!user) {
		return <GenericLoaderPlaceholder />;
	}

	return (
		<div className={"flex flex-col h-full p-4"}>
			<div className="grow flex flex-col items-center justify-center">
				<div className="w-full max-w-md">
					<StepIndicator />
					<div className="bg-surface rounded-xl shadow-lg p-6 mb-6">{renderStep()}</div>
					<div className="flex space-x-4">
						{step > 1 && (
							<div className="flex-0">
								<Button type="outline" onClick={handleBack} disabled={submitting}>
									Zurück
								</Button>
							</div>
						)}
						{step < totalSteps ? (
							<div className="flex-1">
								<Button type="primary" onClick={handleNext} disabled={!isStepValid()}>
									Weiter
								</Button>
							</div>
						) : (
							<div className="flex-1">
								<Button
									type="primary"
									onClick={handleComplete}
									withLoader={submitting}
									disabled={submitting}
								>
									Fertig
								</Button>
							</div>
						)}
					</div>
				</div>
			</div>
			<div className={"shrink-0"}>
				<div className="w-full max-w-md mx-auto text-center text-on-surface-variant text-sm">
					Eingeloggt als
					<span className={"font-semibold ml-1"}>
						{user.firstName} {user.lastName}
					</span>
				</div>
				<div className="w-full max-w-md mx-auto text-center text-on-surface-variant text-sm mb-4 flex flex-row justify-center items-center gap-2">
					Nicht Ihr Konto?
					<Button
						type="link"
						width={"auto"}
						onClick={() => {
							// noinspection JSIgnoredPromiseFromCall
							authService.logout();
						}}
					>
						Logout
					</Button>
				</div>
			</div>
		</div>
	);
}

export default Onboarding;
