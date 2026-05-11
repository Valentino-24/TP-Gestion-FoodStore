import { type FormEvent, useState } from 'react'

// ── Types ──────────────────────────────────────────────────────

export interface AddressFormData {
  calle: string
  numero: string
  ciudad: string
  provincia: string
  codigo_postal: string
  telefono_contacto: string
}

interface Props {
  initialData?: AddressFormData
  onSubmit: (data: AddressFormData) => void
  onCancel?: () => void
  isLoading?: boolean
}

// ── Component ──────────────────────────────────────────────────

export default function AddressForm({ initialData, onSubmit, onCancel, isLoading }: Props) {
  const [form, setForm] = useState<AddressFormData>({
    calle: initialData?.calle ?? '',
    numero: initialData?.numero ?? '',
    ciudad: initialData?.ciudad ?? '',
    provincia: initialData?.provincia ?? '',
    codigo_postal: initialData?.codigo_postal ?? '',
    telefono_contacto: initialData?.telefono_contacto ?? '',
  })
  const [errors, setErrors] = useState<Partial<Record<keyof AddressFormData, string>>>({})

  function validate(): boolean {
    const newErrors: typeof errors = {}
    if (!form.calle.trim()) newErrors.calle = 'La calle es obligatoria'
    if (!form.numero.trim()) newErrors.numero = 'El número es obligatorio'
    if (!form.ciudad.trim()) newErrors.ciudad = 'La ciudad es obligatoria'
    if (!form.provincia.trim()) newErrors.provincia = 'La provincia es obligatoria'
    if (!form.codigo_postal.trim()) newErrors.codigo_postal = 'El código postal es obligatorio'
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (validate()) {
      onSubmit(form)
    }
  }

  function handleChange(field: keyof AddressFormData, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }))
    }
  }

  function fieldClass(field: keyof AddressFormData): string {
    return `w-full rounded-lg border ${errors[field] ? 'border-red-300' : 'border-gray-300'} px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500`
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid gap-4 sm:grid-cols-[1fr_120px]">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Calle</label>
          <input
            className={fieldClass('calle')}
            value={form.calle}
            onChange={(e) => handleChange('calle', e.target.value)}
            placeholder="Av. Corrientes"
          />
          {errors.calle && <p className="mt-1 text-xs text-red-600">{errors.calle}</p>}
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Número</label>
          <input
            className={fieldClass('numero')}
            value={form.numero}
            onChange={(e) => handleChange('numero', e.target.value)}
            placeholder="1234"
          />
          {errors.numero && <p className="mt-1 text-xs text-red-600">{errors.numero}</p>}
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Ciudad</label>
          <input
            className={fieldClass('ciudad')}
            value={form.ciudad}
            onChange={(e) => handleChange('ciudad', e.target.value)}
            placeholder="Buenos Aires"
          />
          {errors.ciudad && <p className="mt-1 text-xs text-red-600">{errors.ciudad}</p>}
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Provincia</label>
          <input
            className={fieldClass('provincia')}
            value={form.provincia}
            onChange={(e) => handleChange('provincia', e.target.value)}
            placeholder="CABA"
          />
          {errors.provincia && <p className="mt-1 text-xs text-red-600">{errors.provincia}</p>}
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Código Postal</label>
          <input
            className={fieldClass('codigo_postal')}
            value={form.codigo_postal}
            onChange={(e) => handleChange('codigo_postal', e.target.value)}
            placeholder="C1043"
          />
          {errors.codigo_postal && <p className="mt-1 text-xs text-red-600">{errors.codigo_postal}</p>}
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Teléfono de contacto</label>
          <input
            className={fieldClass('telefono_contacto')}
            value={form.telefono_contacto}
            onChange={(e) => handleChange('telefono_contacto', e.target.value)}
            placeholder="+54 11 1234-5678"
          />
        </div>
      </div>

      <div className="flex justify-end gap-3">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Cancelar
          </button>
        )}
        <button
          type="submit"
          disabled={isLoading}
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {isLoading ? 'Guardando...' : initialData ? 'Actualizar' : 'Agregar dirección'}
        </button>
      </div>
    </form>
  )
}
