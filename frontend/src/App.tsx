import { useState } from "react"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

type Period = "month" | "quarter" | "half-year" | "year"

function App() {
  const [period, setPeriod] = useState<Period>("month")

  return (
    <div className="mx-auto max-w-3xl p-8">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Money Map</CardTitle>
          <Select value={period} onValueChange={(v) => setPeriod(v as Period)}>
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="month">Miesiąc</SelectItem>
              <SelectItem value="quarter">Kwartał</SelectItem>
              <SelectItem value="half-year">Półrocze</SelectItem>
              <SelectItem value="year">Rok</SelectItem>
            </SelectContent>
          </Select>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <p className="text-sm text-muted-foreground">
            Placeholder na Sankey i wykresy. Backend jeszcze nie podłączony.
          </p>
          <Button>Importuj wyciąg</Button>
        </CardContent>
      </Card>
    </div>
  )
}

export default App
