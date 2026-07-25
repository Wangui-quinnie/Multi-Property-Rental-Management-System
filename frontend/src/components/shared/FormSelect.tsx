import type { ComponentProps, ReactNode } from "react";
import { Select } from "@/components/ui/select";
import { FormField } from "@/components/shared/FormField";

interface FormSelectProps extends ComponentProps<typeof Select> {
  label: string;
  error?: string;
  required?: boolean;
  containerClassName?: string;
  children: ReactNode; // <option> elements
}

export function FormSelect({
  label,
  error,
  required,
  containerClassName,
  id,
  name,
  children,
  ...selectProps
}: FormSelectProps) {
  const selectId = id ?? name;

  if (!selectId) {
    throw new Error("FormSelect requires either an `id` or a `name` prop.");
  }

  return (
    <FormField
      label={label}
      htmlFor={selectId}
      error={error}
      required={required}
      className={containerClassName}
    >
      <Select
        id={selectId}
        name={name}
        aria-invalid={!!error}
        aria-describedby={error ? `${selectId}-error` : undefined}
        {...selectProps}
      >
        {children}
      </Select>
    </FormField>
  );
}