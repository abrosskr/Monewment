"use client";
import React, { createContext, useContext, useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";

const LayoutContext = createContext({ isClientMode: false });

export const useLayoutContext = () => useContext(LayoutContext);

function ContextProvider({ children }: { children: React.ReactNode }) {
    const searchParams = useSearchParams();
    const [isClientMode, setIsClientMode] = useState(false);

    useEffect(() => {
        if (searchParams.get("context") === "client") {
            setIsClientMode(true);
            // Also store in session storage to persist across navigation in the same tab
            sessionStorage.setItem("monewment_ui_context", "client");
        } else if (sessionStorage.getItem("monewment_ui_context") === "client") {
            setIsClientMode(true);
        }
    }, [searchParams]);

    return (
        <LayoutContext.Provider value={{ isClientMode }}>
            {children}
        </LayoutContext.Provider>
    );
}

export default function LayoutProvider({ children }: { children: React.ReactNode }) {
    return (
        <Suspense fallback={children}>
            <ContextProvider>{children}</ContextProvider>
        </Suspense>
    );
}
