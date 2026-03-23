import { MessageCard as MessageCardType } from "@/lib/mock-data";
import { Plane, ArrowRight, Star, ShieldCheck, ShieldAlert, Download, UtensilsCrossed, Users, DoorOpen } from "lucide-react";

export function MessageCardRenderer({ card }: { card: MessageCardType }) {
  switch (card.type) {
    case "flight": return <FlightCard data={card.data} />;
    case "hotel": return <HotelCard data={card.data} />;
    case "restaurant": return <RestaurantCard data={card.data} />;
    case "approval": return <ApprovalCard data={card.data} />;
    case "compliance": return <ComplianceCard data={card.data} />;
    default: return null;
  }
}

function FlightCard({ data }: { data: any }) {
  return (
    <div className="mt-3 rounded-lg border bg-card p-4 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-center gap-2 text-xs text-muted-foreground mb-3">
        <Plane className="w-3.5 h-3.5 text-primary" />
        <span>{data.airline}</span>
        <span className="ml-auto">{data.date}</span>
      </div>
      <div className="flex items-center justify-between">
        <div className="text-center">
          <div className="text-2xl font-bold tracking-tight">{data.departure}</div>
          <div className="text-sm text-muted-foreground">{data.from} {data.fromCode}</div>
        </div>
        <div className="flex-1 flex items-center justify-center px-4">
          <div className="h-px flex-1 bg-border" />
          <ArrowRight className="w-4 h-4 mx-2 text-primary" />
          <div className="h-px flex-1 bg-border" />
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold tracking-tight">{data.arrival}</div>
          <div className="text-sm text-muted-foreground">{data.to} {data.toCode}</div>
        </div>
      </div>
      <div className="flex items-center justify-between mt-3 pt-3 border-t">
        <span className="text-lg font-semibold text-primary">¥{data.price}</span>
        {data.compliant && (
          <span className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-accent text-accent-foreground">
            <ShieldCheck className="w-3 h-3" /> 合规
          </span>
        )}
      </div>
    </div>
  );
}

function HotelCard({ data }: { data: any }) {
  return (
    <div className="mt-3 rounded-lg border bg-card overflow-hidden shadow-sm hover:shadow-md transition-shadow">
      <img src={data.image} alt={data.name} className="w-full h-32 object-cover" loading="lazy" />
      <div className="p-4">
        <div className="flex items-start justify-between">
          <div>
            <h4 className="font-semibold text-sm">{data.name}</h4>
            <div className="flex items-center gap-1 mt-1">
              {Array.from({ length: data.stars }).map((_, i) => (
                <Star key={i} className="w-3 h-3 fill-primary text-primary" />
              ))}
            </div>
          </div>
          <div className="text-right">
            <div className="text-lg font-bold text-primary">¥{data.price}<span className="text-xs font-normal text-muted-foreground">/晚</span></div>
          </div>
        </div>
        <p className="text-xs text-muted-foreground mt-2">{data.distance}</p>
        {!data.compliant && (
          <div className="mt-2 flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-destructive/10 text-destructive w-fit">
            <ShieldAlert className="w-3 h-3" /> 超标 ¥{data.overBudget}/晚
          </div>
        )}
      </div>
    </div>
  );
}

function RestaurantCard({ data }: { data: any }) {
  return (
    <div className="mt-3 rounded-lg border bg-card p-4 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-2">
        <h4 className="font-semibold text-sm">{data.name}</h4>
        <span className="text-xs text-muted-foreground flex items-center gap-1">
          <Star className="w-3 h-3 fill-primary text-primary" /> {data.rating}
        </span>
      </div>
      <div className="flex gap-3 text-xs text-muted-foreground">
        <span className="flex items-center gap-1"><UtensilsCrossed className="w-3 h-3" />{data.cuisine}</span>
        <span className="flex items-center gap-1"><Users className="w-3 h-3" />{data.capacity}</span>
        {data.hasPrivateRoom && (
          <span className="flex items-center gap-1"><DoorOpen className="w-3 h-3" />有包间</span>
        )}
      </div>
      <div className="mt-3 pt-3 border-t">
        <span className="text-primary font-semibold">¥{data.pricePerPerson}</span>
        <span className="text-xs text-muted-foreground">/人均</span>
      </div>
    </div>
  );
}

function ApprovalCard({ data }: { data: any }) {
  return (
    <div className="mt-3 rounded-lg border bg-card p-4 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-3">
        <h4 className="font-semibold text-sm">出差审批单</h4>
        <span className="text-xs px-2 py-0.5 rounded-full bg-accent text-accent-foreground">{data.status}</span>
      </div>
      <div className="space-y-2">
        {data.items.map((item: any, i: number) => (
          <div key={i} className="flex justify-between text-sm">
            <span className="text-muted-foreground">{item.name}</span>
            <span className="tabular-nums">¥{item.amount.toLocaleString()}</span>
          </div>
        ))}
      </div>
      <div className="flex items-center justify-between mt-3 pt-3 border-t">
        <span className="font-bold">合计：<span className="text-primary text-lg">¥{data.total.toLocaleString()}</span></span>
        <button className="inline-flex items-center gap-1 text-xs px-3 py-1.5 rounded-md bg-primary text-primary-foreground hover:bg-primary/90 transition-colors active:scale-[0.97]">
          <Download className="w-3 h-3" /> 导出
        </button>
      </div>
    </div>
  );
}

function ComplianceCard({ data }: { data: any }) {
  const isWarning = data.level === "warning";
  return (
    <div className={`mt-3 rounded-lg border p-4 shadow-sm ${isWarning ? "border-primary/30 bg-primary/5" : "border-destructive/30 bg-destructive/5"}`}>
      <div className="flex items-center gap-2 mb-2">
        <ShieldAlert className={`w-4 h-4 ${isWarning ? "text-primary" : "text-destructive"}`} />
        <span className={`font-semibold text-sm ${isWarning ? "text-primary" : "text-destructive"}`}>{data.message}</span>
      </div>
      <p className="text-sm text-muted-foreground">{data.detail}</p>
      {data.suggestion && (
        <p className="text-sm mt-2 text-foreground">💡 {data.suggestion}</p>
      )}
    </div>
  );
}
