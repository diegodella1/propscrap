import { redirect } from "next/navigation";

import { getCurrentUserFromSession } from "../../../lib/session";

export default async function LegacyAdminPage() {
  const currentUser = await getCurrentUserFromSession();
  if (!currentUser) {
    redirect("/login");
  }
  if (currentUser.role === "admin") {
    redirect("/admin/platform");
  }
  if (currentUser.role === "manager") {
    redirect("/admin/company");
  }
  redirect("/dashboard");
}
