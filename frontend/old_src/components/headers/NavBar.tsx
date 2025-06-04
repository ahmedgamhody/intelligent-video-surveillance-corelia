import { Navbar } from "flowbite-react";

import { Link } from "react-router-dom";
import { Bell, LayoutDashboard, User } from "lucide-react";

export function NavBar() {
  return (
    <div className="px-4 bg-black ">
      <Navbar fluid rounded className="bg-black">
        <Navbar.Brand as={Link} to="/" className="text-white">
          <h1 className="text-3xl font-bold">IVS</h1>
        </Navbar.Brand>

        <div className="flex gap-5 items-center">
          <Navbar.Toggle />
        </div>
        <div className="hidden md:flex gap-4 items-center">
          <LayoutDashboard
            color="white"
            strokeWidth={3}
            className="cursor-pointer"
          />
          <Bell color="white" strokeWidth={3} className="cursor-pointer" />
          <User color="white" strokeWidth={3} className="cursor-pointer" />
        </div>
      </Navbar>
    </div>
  );
}
