'use client';
import UIRenderer from '@/components/ui-engine/Renderer';

// [Auto-Generated] Server-Driven UI Schema
const SCHEMA = {
  "type": "container",
  "style": {
    "className": "bg-blue-900 p-10 text-white rounded-xl"
  },
  "children": [
    {
      "type": "text",
      "props": {
        "type": "title",
        "content": "BOM Fix Success!"
      }
    },
    {
      "type": "button",
      "props": {
        "label": "Perfect",
        "variant": "primary"
      }
    }
  ]
};

export default function DirectTest() {
  return <UIRenderer schema={SCHEMA} />;
}
