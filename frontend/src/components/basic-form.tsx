import { type ReactNode, useState } from "react";
import { MdInfoOutline } from "react-icons/md";
import Button from "@/components/button";
import type { Awaitable } from "@/services/awaitable";
import { DomainError } from "@/services/http-client";

type BasicFormProps = {
	submitText: string;
	isDisabled: boolean;
	onSubmit: () => Awaitable<void>;
	children: ReactNode;
	isReadOnly?: boolean;
};

export default function BasicForm(props: BasicFormProps) {
	const [submitting, setSubmitting] = useState(false);
	const [error, setError] = useState<string | null>(null);

	const onSubmit = async () => {
		if (submitting) return;

		setSubmitting(true);
		try {
			await props.onSubmit();
			setError(null);
		} catch (e) {
			if (e instanceof DomainError) {
				setError(e.detail || "Ein unbekannter Fehler ist aufgetreten.");
				return;
			}
			setError((e as Error).message || "Ein unbekannter Fehler ist aufgetreten.");
		} finally {
			setSubmitting(false);
		}
	};

	return (
		<>
			<fieldset disabled={props.isReadOnly}>{props.children}</fieldset>
			{error && (
				<div
					className={
						"flex flex-col bg-error-container text-on-error-container p-4 rounded-md mt-4 border border-error border-2"
					}
				>
					<div className={"flex flex-row items-center gap-2"}>
						<MdInfoOutline className={"shrink-0"} size={"1.2em"} />
						<p className={"font-medium"}>Ein Fehler is aufgetreten</p>
					</div>
					<div className={"mt-2"}>{error}</div>
				</div>
			)}
			<Button
				type="primary"
				onClick={onSubmit}
				disabled={props.isDisabled || props.isReadOnly}
				withLoader={submitting}
			>
				{props.submitText}
			</Button>
		</>
	);
}
