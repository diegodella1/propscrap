import { redirect } from "next/navigation";

import { PlatformAdminPage } from "../../../components/platform-admin-page";
import {
  fetchAdminAuditEvents,
  fetchAdminCompanyProfiles,
  fetchAdminCompanySourceAccess,
  fetchAdminSources,
  fetchAlerts,
  fetchAutomationSettings,
  fetchSourceRuns,
  fetchUsers,
  fetchWhatsappOutbox,
} from "../../../lib/api";
import { getCookieHeaderFromSession, getCurrentUserFromSession } from "../../../lib/session";

export default async function PlatformAdminRoute() {
  const [currentUser, cookieHeader] = await Promise.all([
    getCurrentUserFromSession(),
    getCookieHeaderFromSession(),
  ]);

  if (!currentUser) {
    redirect("/login");
  }
  if (currentUser.role !== "admin") {
    redirect(currentUser.role === "manager" ? "/admin/company" : "/dashboard");
  }

  const [sourceRuns, alerts, users, sources, automationSettings, whatsappOutbox, auditEvents, companyProfiles] = await Promise.all([
    fetchSourceRuns(cookieHeader || undefined),
    fetchAlerts(cookieHeader || undefined),
    fetchUsers(cookieHeader || undefined),
    fetchAdminSources(cookieHeader || undefined),
    fetchAutomationSettings(cookieHeader || undefined),
    fetchWhatsappOutbox(cookieHeader || undefined),
    fetchAdminAuditEvents(cookieHeader || undefined),
    fetchAdminCompanyProfiles(cookieHeader || undefined),
  ]);

  const companySourceAccess = await Promise.all(
    companyProfiles.map((profile) => fetchAdminCompanySourceAccess(profile.id, cookieHeader || undefined)),
  );

  return (
    <PlatformAdminPage
      currentUserName={currentUser.full_name}
      sourceRuns={sourceRuns}
      alerts={alerts}
      users={users}
      sources={sources}
      automationSettings={automationSettings}
      whatsappOutbox={whatsappOutbox}
      auditEvents={auditEvents}
      companyProfiles={companyProfiles}
      companySourceAccess={companySourceAccess}
    />
  );
}
