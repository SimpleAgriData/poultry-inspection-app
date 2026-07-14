import { useLayoutEffect, useRef, useState } from "react";

const resizeStyles = {
	both: "resize",
	horizontal: "resize-x",
	vertical: "resize-y",
	none: "resize-none",
};

interface TextAreaProps {
	label?: string;
	value: string;
	onChange: (value: string) => void;
	placeholder?: string;
	disabled?: boolean;
	description?: string;
	required?: boolean;
	invalid?: boolean;
	errorMessage?: string;
	minRows?: number;
	autoResize?: boolean;
	resizable?: "none" | "both" | "horizontal" | "vertical";
}

export default function TextArea({
	label,
	value,
	onChange,
	placeholder,
	disabled,
	description,
	required,
	invalid,
	errorMessage,
	minRows,
	autoResize,
	resizable,
}: TextAreaProps) {
	const ref = useRef<HTMLTextAreaElement>(null);
	const [hadFocus, setHadFocus] = useState(false);

	// biome-ignore lint/correctness/useExhaustiveDependencies: In the special case that the values change, we want to trigger the resize effect to adjust the height accordingly. Otherwise, this would only run on mount, which is not sufficient for our use case.
	useLayoutEffect(() => {
		const element = ref.current;
		if (!element) return;

		const resize = () => {
			if (!autoResize) return;
			element.style.height = "auto"; // Reset height to get the correct scrollHeight
			const newHeight = element.scrollHeight;
			element.style.height = `${newHeight}px`;
		};

		resize(); // Initial resize

		element.addEventListener("input", resize);
		window.addEventListener("resize", resize); // Handle window resize

		return () => {
			element.removeEventListener("input", resize);
			window.removeEventListener("resize", resize);
		};
	}, [autoResize, value]);

	const resizeClass = resizable ? resizeStyles[resizable] : "resize-none";
	const hasValue = value.trim() !== "";
	const hasError = invalid ?? (required && hadFocus && !hasValue);
	const errorStyles = hasError
		? "border-error focus-within:border-red-500 focus-within:ring-error/30 ring-2 ring-error/30"
		: "border-outline focus-within:border-primary focus-within:ring-primary/30";

	const onBlur = () => {
		if (!hadFocus) {
			setHadFocus(true);
		}
	};

	return (
		<div>
			{label && (
				<label
					htmlFor={`input-${label}`}
					className="block mb-2 text-base font-medium text-on-secondary-container"
				>
					{label}
				</label>
			)}
			<textarea
				ref={ref}
				id={label ? `input-${label}` : undefined}
				onBlur={onBlur}
				className={`bg-background border text-on-surface text-base rounded-lg outline-0 shadow-lg block w-full p-2.5 disabled:bg-surface-disabled
					disabled:text-on-surface-disabled disabled:cursor-not-allowed
					focus:ring-2
					${errorStyles}
					${autoResize ? "overflow-hidden" : "overflow-auto"}
					${resizeClass}
					`}
				value={value}
				onChange={(e) => onChange(e.target.value)}
				placeholder={placeholder}
				disabled={disabled}
				rows={minRows || 4}
			/>
			{hasError && errorMessage && <p className="mt-1 text-xs text-error">{errorMessage}</p>}
			{description && <p className="mt-2 text-xs text-on-secondary-container">{description}</p>}
		</div>
	);
}
