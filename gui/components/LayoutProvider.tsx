"use client";
import React, { createContext, useContext, useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";

const LayoutContext = createContext({ isClientMode: false });

export const useLayoutContext = () => useContext(LayoutContext);

function ContextProvider({ children }: { children: React.ReactNode }) {
    const searchParams = useSearchParams();
    const [isClientMode, setIsClientMode] = useState(false);

    useEffect(() => {
        const contextParam = searchParams.get("context");
        const storedContext = sessionStorage.getItem("monewment_ui_context");

        if (contextParam === "client" && !isClientMode) {
            setIsClientMode(true);
            sessionStorage.setItem("monewment_ui_context", "client");
        } else if (storedContext === "client" && !isClientMode) {
            setIsClientMode(true);
        }
    }, [searchParams, isClientMode]);

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
