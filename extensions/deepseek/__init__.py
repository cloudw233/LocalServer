from openai import AsyncOpenAI
from config import config

import asyncio

async def get_deepseek_anwser(question: str) -> str:
    """
    调用deepseek-ai回答问题
    :param question: 问题
    :return: 回答
    """
    try:
        client = AsyncOpenAI(
            base_url = "https://api.siliconflow.cn/v1/",
            api_key = config('siliconflow_api_key')
        )

        response = await client.chat.completions.create(
            model = 'deepseek-ai/DeepSeek-V3',
            messages=[{"role": "user", "content": question + '，请尽量简短回答，50字以内。'}],
            stream=False,
            max_tokens=1024
        )

        return response.choices[0].message.content
    except Exception:
        temp = {'心绞痛': '心绞痛发作时，应立即停止活动，坐下或躺下休息，服用硝酸甘油片，并及时就医。',
                '阿尔茨海默': '阿尔茨海默症需早期诊断，药物治疗结合认知训练，改善生活品质。保持健康饮食、规律运动，心理支持，及时就医。',
                '糖尿病': '糖尿病需控制饮食，适量运动，监测血糖，遵医嘱用药，定期检查，保持健康生活方式。',
                '高血压': '高血压需控制饮食（低盐低脂）、适量运动、戒烟限酒、保持健康体重，遵医嘱用药，定期监测血压。',
                '冠心病': '冠心病需药物治疗（如硝酸酯类、他汀类）、改善生活方式（低脂低盐饮食、戒烟限酒、适量运动），定期复查，遵医嘱调整治疗方案。',
                }
        for k in temp.keys():
            if k in question:
                return temp[k]
        return '抱歉，我不知道该问题的答案。'


if __name__ == '__main__':
    print(asyncio.run(get_deepseek_anwser("怎么看美俄结盟")))