'use client';
import UIRenderer from '@/components/ui-engine/Renderer';

// [Auto-Generated] Server-Driven UI Schema
const SCHEMA = {
  "type": "container",
  "style": {
    "className": "w-[400px] bg-[#202020] border border-[#333] rounded-lg shadow-2xl mx-auto mt-20"
  },
  "children": [
    {
      "type": "text",
      "props": {
        "type": "title",
        "content": "Monewment Login"
      }
    },
    {
      "type": "text",
      "props": {
        "content": "보안을 위해 계정 정보를 입력해주세요."
      }
    },
    {
      "type": "container",
      "style": {
        "className": "mt-6 space-y-3"
      },
      "children": [
        {
          "type": "input",
          "props": {
            "placeholder": "user@example.com"
          }
        },
        {
          "type": "input",
          "props": {
            "type": "password",
            "placeholder": "Password"
          }
        }
      ]
    },
    {
      "type": "container",
      "style": {
        "className": "mt-6 flex justify-end"
      },
      "children": [
        {
          "type": "button",
          "props": {
            "variant": "secondary",
            "label": "취소"
          }
        },
        {
          "type": "container",
          "style": {
            "className": "w-2"
          }
        },
        {
          "type": "button",
          "props": {
            "variant": "primary",
            "label": "로그인"
          }
        }
      ]
    }
  ]
};

export default function LoginBox() {
  return <UIRenderer schema={SCHEMA} />;
}
