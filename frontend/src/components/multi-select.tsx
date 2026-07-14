"use client";

import { Subtitled } from "@/components/subtitled";

type Primitive = string | number;

interface MultiSelectOption<T extends Primitive> {
	value: T;
	label: string;
}

interface MultiSelectProps<T extends Primitive> {
	label?: string;
	values: T[];
	options: MultiSelectOption<T>[];
	onChange: (values: T[]) => void;
	description?: string;
	disabled?: boolean;
}

function MultiSelect<T extends Primitive>({
	label,
	values,
	options,
	onChange,
	description,
	disabled = false,
}: MultiSelectProps<T>) {
	const toggleValue = (value: T) => {
		if (disabled) {
			return;
		}

		if (values.includes(value)) {
			onChange(values.filter((v) => v !== value));
		} else {
			onChange([...values, value]);
		}
	};

	return (
		<div className="space-y-2">
			{label && (
				<span className="block text-base font-medium text-on-secondary-container">{label}</span>
			)}
			<Subtitled subtitle={description}>
				<div className="flex flex-wrap gap-2">
					{options.map((option) => {
						const isActive = values.includes(option.value);
						return (
							<button
								key={option.value}
								type="button"
								onClick={() => toggleValue(option.value)}
								disabled={disabled}
								className={`rounded-md border px-3 py-2 text-sm font-medium transition-colors ${
									isActive
										? "border-primary bg-primary-container text-primary"
										: "border-outline bg-background text-on-surface hover:border-on-surface-variant"
								} ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
							>
								{option.label}
							</button>
						);
					})}
				</div>
			</Subtitled>
		</div>
	);
}

export type { MultiSelectOption };
export default MultiSelect;
