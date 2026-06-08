interface Props {
  page: number
  size: number
  total: number
  onPageChange: (page: number) => void
}

export default function Pagination({ page, size, total, onPageChange }: Props) {
  const totalPages = Math.ceil(total / size)
  if (totalPages <= 1) return null

  const start = (page - 1) * size + 1
  const end = Math.min(page * size, total)

  // Build page numbers to show
  const pages: number[] = []
  const maxVisible = 5
  let startPage = Math.max(1, page - Math.floor(maxVisible / 2))
  const endPage = Math.min(totalPages, startPage + maxVisible - 1)
  if (endPage - startPage + 1 < maxVisible) {
    startPage = Math.max(1, endPage - maxVisible + 1)
  }
  for (let i = startPage; i <= endPage; i++) {
    pages.push(i)
  }

  return (
    <div className="mt-8 flex flex-col items-center gap-3 sm:flex-row sm:justify-between">
      <p className="text-sm text-gray-600">
        Mostrando {start}-{end} de {total} productos
      </p>

      <div className="flex items-center gap-1">
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={page <= 1}
          className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40"
        >
          Anterior
        </button>

        {startPage > 1 && (
          <>
            <button
              onClick={() => onPageChange(1)}
              className="rounded-lg px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100"
            >
              1
            </button>
            {startPage > 2 && <span className="px-1 text-gray-400">...</span>}
          </>
        )}

        {pages.map((p) => (
          <button
            key={p}
            onClick={() => onPageChange(p)}
            className={`rounded-lg px-3 py-1.5 text-sm font-medium ${
              p === page
                ? 'bg-blue-600 text-white'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            {p}
          </button>
        ))}

        {endPage < totalPages && (
          <>
            {endPage < totalPages - 1 && <span className="px-1 text-gray-400">...</span>}
            <button
              onClick={() => onPageChange(totalPages)}
              className="rounded-lg px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100"
            >
              {totalPages}
            </button>
          </>
        )}

        <button
          onClick={() => onPageChange(page + 1)}
          disabled={page >= totalPages}
          className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40"
        >
          Siguiente
        </button>
      </div>
    </div>
  )
}
