'use client';
import UIRenderer from '@/components/ui-engine/Renderer';

// [Auto-Generated] Server-Driven UI Schema
const SCHEMA = {
  "type": "container",
  "style": {
    "className": "w-[350px] bg-[#222] border border-[#444] rounded-xl shadow-lg p-6"
  },
  "children": [
    {
      "type": "text",
      "props": {
        "type": "title",
        "content": "Clean Reset Test"
      }
    },
    {
      "type": "input",
      "props": {
        "placeholder": "ID"
      }
    },
    {
      "type": "input",
      "props": {
        "type": "password",
        "placeholder": "PW"
      }
    },
    {
      "type": "container",
      "style": {
        "className": "mt-4 flex justify-end"
      },
      "children": [
        {
          "type": "button",
          "props": {
            "label": "Login",
            "variant": "primary"
          }
        }
      ]
    }
  ]
};

export default function CleanTest() {
  return <UIRenderer schema={SCHEMA} />;
}
