"use client";

import { MdCheck, MdClose } from "react-icons/md";

interface ToggleSwitchProps {
	checked: boolean;
	onChange: (checked: boolean) => void;
	label?: string;
	disabled?: boolean;
}

function ToggleSwitch({ checked, onChange, label, disabled = false }: ToggleSwitchProps) {
	return (
		<div className="flex items-center gap-3">
			{label && <span className="min-w-24 text-sm font-medium text-on-surface">{label}</span>}
			<button
				type="button"
				onClick={() => !disabled && onChange(!checked)}
				disabled={disabled}
				className={`relative flex items-center h-6 w-14 rounded-md border border-outline shadow-sm bg-background overflow-hidden
					${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
			>
				<div
					className={`absolute top-0 h-full w-1/2 rounded transition-all duration-200 ease-in-out ${
						checked ? "left-0 bg-primary-container" : "left-1/2 bg-error-container"
					}`}
				/>
				<div className="relative z-10 flex items-center justify-center w-1/2">
					<MdCheck
						className={`size-4 transition-colors duration-200 ${checked ? "text-primary" : "text-outline"}`}
					/>
				</div>
				<div className="relative z-10 flex items-center justify-center w-1/2">
					<MdClose
						className={`size-4 transition-colors duration-200 ${checked ? "text-outline" : "text-error"}`}
					/>
				</div>
			</button>
		</div>
	);
}

export default ToggleSwitch;
