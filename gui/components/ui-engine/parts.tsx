'use client';
import React from 'react';

// [컨테이너]
export const Container = ({ children, style }: any) => (
  <div className={`p-4 ${style?.className}`} style={style?.custom}>
    {children}
  </div>
);

// [버튼]
export const Button = ({ label, variant, onClick }: any) => {
  const baseStyle = "px-4 py-2 rounded font-bold transition-all active:scale-95";
  const styles: any = {
    primary: "bg-[#3B82F6] text-white hover:bg-blue-600",
    secondary: "bg-[#404040] text-white hover:bg-[#505050]",
    danger: "bg-red-500 text-white hover:bg-red-600",
  };
  return (
    <button className={`${baseStyle} ${styles[variant || 'primary']}`} onClick={onClick}>
      {label}
    </button>
  );
};

// [텍스트]
export const Text = ({ content, type }: any) => {
  if (type === 'title') return <h2 className="text-xl font-bold text-white mb-2">{content}</h2>;
  return <p className="text-sm text-gray-400">{content}</p>;
};

// [입력창]
export const Input = ({ placeholder, type = "text" }: any) => (
  <input type={type} placeholder={placeholder} className="w-full bg-[#1A1A1A] border border-[#333] text-white px-3 py-2 rounded focus:outline-none focus:border-[#FFD700] mb-2"/>
);

export const COMPONENT_MAP: any = { container: Container, button: Button, text: Text, input: Input };
