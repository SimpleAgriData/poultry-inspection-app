"use client";

import { useRouter } from "next/navigation";
import type React from "react";
import { MdArrowBack } from "react-icons/md";
import { PageLayout } from "@/components/page-layout";

interface SubPageLayoutProps {
	backLink?: string;
	title: string | React.ReactNode;
	subtitle?: string | React.ReactNode;
	actionRight?: React.ReactNode;
	children?: React.ReactNode;
}

export default function SubPageLayout(props: SubPageLayoutProps) {
	const router = useRouter();

	const handleBackClick = () => {
		if (props.backLink) {
			router.replace(props.backLink);
		} else {
			router.back();
		}
	};

	return (
		<PageLayout>
			<div className="w-full max-w-md mb-4 text-on-secondary-container">
				<button
					type="button"
					onClick={handleBackClick}
					className="inline-flex items-center content-center gap-1 font-medium text-on-surface hover:cursor-pointer"
				>
					<MdArrowBack className="size-6" />
					<span className="pt-0.5">Zurück</span>
				</button>
			</div>
			<div className="w-full max-w-md mb-6">
				<div className="flex flex-row items-center justify-between gap-4">
					<h1 className="text-2xl font-bold text-on-surface w-full max-w-md">{props.title}</h1>
					{props.actionRight ? <div className="ml-auto">{props.actionRight}</div> : null}
				</div>
				{props.subtitle ? (
					<p className="text-on-surface-variant font-medium">{props.subtitle}</p>
				) : null}
			</div>
			<div className="w-full max-w-md space-y-6">{props.children}</div>
		</PageLayout>
	);
}
