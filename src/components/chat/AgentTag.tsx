import { agents } from "@/lib/mock-data";

export function AgentTag({ agentId, size = "sm" }: { agentId: string; size?: "sm" | "md" }) {
  const agent = agents.find(a => a.id === agentId);
  if (!agent) return null;

  const Icon = agent.icon;
  const sizeClasses = size === "sm"
    ? "text-xs px-2 py-0.5 gap-1"
    : "text-sm px-3 py-1 gap-1.5";

  return (
    <span className={`inline-flex items-center rounded-full bg-accent text-accent-foreground font-medium ${sizeClasses}`}>
      <Icon className={size === "sm" ? "w-3 h-3" : "w-4 h-4"} />
      {agent.name}
    </span>
  );
}
