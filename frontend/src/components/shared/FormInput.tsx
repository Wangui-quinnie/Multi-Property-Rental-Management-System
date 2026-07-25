import type { ComponentProps } from "react";
import { Input } from "@/components/ui/input";
import { FormField } from "@/components/shared/FormField";

interface FormInputProps extends ComponentProps<typeof Input> {
  label: string;
  error?: string;
  required?: boolean;
  containerClassName?: string;
}

/**
 * Convenience combo of FormField + Input for the common controlled
 * text/email/password/number input case. For anything else (Select,
 * Textarea, checkboxes) wrap the control directly in `FormField` instead.
 */
export function FormInput({
  label,
  error,
  required,
  containerClassName,
  id,
  name,
  ...inputProps
}: FormInputProps) {
  const inputId = id ?? name;

  if (!inputId) {
    throw new Error("FormInput requires either an `id` or a `name` prop.");
  }

  return (
    <FormField
      label={label}
      htmlFor={inputId}
      error={error}
      required={required}
      className={containerClassName}
    >
      <Input
        id={inputId}
        name={name}
        aria-invalid={!!error}
        aria-describedby={error ? `${inputId}-error` : undefined}
        {...inputProps}
      />
    </FormField>
  );
}
