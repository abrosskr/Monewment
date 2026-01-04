'use client';
import React from 'react';
import { COMPONENT_MAP } from './parts';

const renderComponent = (config: any, index: number) => {
  const Component = COMPONENT_MAP[config.type];
  if (!Component) return <div key={index} className="text-red-500">Unknown: {config.type}</div>;
  
  // [복구됨] 자식 요소 재귀 렌더링 코드
  const children = config.children?.map((child: any, idx: number) => 
    renderComponent(child, idx)
  );

  return (
    <Component key={index} {...config.props} style={config.style}>
      {children}
    </Component>
  );
};

export default function UIRenderer({ schema }: { schema: any }) {
  if (!schema) return null;
  return <>{renderComponent(schema, 0)}</>;
}
