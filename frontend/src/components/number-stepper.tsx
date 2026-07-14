"use client";

import { MdAdd, MdRemove } from "react-icons/md";

interface NumberStepperProps {
	value: number;
	onChange: (value: number) => void;
	min?: number;
	max?: number;
	label?: string;
	disabled?: boolean;
}

function NumberStepper({
	value,
	onChange,
	min = 1,
	max = 99,
	label,
	disabled = false,
}: NumberStepperProps) {
	const handleDecrement = () => {
		if (!disabled && value > min) onChange(value - 1);
	};

	const handleIncrement = () => {
		if (!disabled && value < max) onChange(value + 1);
	};

	return (
		<div className="flex flex-col w-full">
			{label && (
				<span className={`font-medium text-on-secondary-container text-base mb-2`}>{label}</span>
			)}
			<div
				className={`flex items-center bg-background border border-outline rounded-md shadow-sm w-full  focus-within:border-primary focus-within:ring-2 focus-within:ring-primary/30
				${disabled ? "opacity-50" : ""}`}
			>
				<button
					type="button"
					onClick={handleDecrement}
					disabled={disabled || value <= min}
					className={`flex items-center justify-center p-3 border-r border-outline
						${disabled || value <= min ? "cursor-not-allowed opacity-50" : "cursor-pointer hover:bg-surface-variant active:bg-surface-variant"}`}
				>
					<MdRemove className="size-5 text-on-surface" />
				</button>
				<div className="flex-1 text-center font-medium text-sm text-on-surface py-3">{value}</div>
				<button
					type="button"
					onClick={handleIncrement}
					disabled={disabled || value >= max}
					className={`flex items-center justify-center p-3 border-l border-outline
						${disabled || value >= max ? "cursor-not-allowed opacity-50" : "cursor-pointer hover:bg-surface-variant active:bg-surface-variant"}`}
				>
					<MdAdd className="size-5 text-on-surface" />
				</button>
			</div>
		</div>
	);
}

export default NumberStepper;
