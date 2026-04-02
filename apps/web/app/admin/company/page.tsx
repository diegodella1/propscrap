import { redirect } from "next/navigation";

import { CompanyAdminPage } from "../../../components/company-admin-page";
import { fetchUsers } from "../../../lib/api";
import { getCookieHeaderFromSession, getCurrentUserFromSession } from "../../../lib/session";

export default async function CompanyAdminRoute() {
  const [currentUser, cookieHeader] = await Promise.all([
    getCurrentUserFromSession(),
    getCookieHeaderFromSession(),
  ]);

  if (!currentUser) {
    redirect("/login");
  }
  if (currentUser.role === "admin") {
    redirect("/admin/platform");
  }
  if (currentUser.role !== "manager") {
    redirect("/dashboard");
  }

  const users = await fetchUsers(cookieHeader || undefined);
  return <CompanyAdminPage currentUserName={currentUser.full_name} users={users} />;
}
