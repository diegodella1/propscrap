import { WorkspaceAdoptionBar } from "../../components/workspace-adoption-bar";

export default async function WorkspaceLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="route-shell route-shell--workspace">
      <WorkspaceAdoptionBar />
      {children}
    </div>
  );
}
