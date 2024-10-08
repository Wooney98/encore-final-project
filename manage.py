#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import torch
from kobert.pytorch_kobert import get_pytorch_kobert_model


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Team_Final_Project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    device = torch.device("cuda:0")
    bertmodel, _= get_pytorch_kobert_model()
    class BERTClassifier(torch.nn.Module):
        def __init__(self,
                    bert,
                    hidden_size = 768,
                    num_classes=8,
                    dr_rate=None,
                    params=None):
            super(BERTClassifier, self).__init__()
            self.bert = bert
            self.dr_rate = dr_rate
                    
            self.classifier = torch.nn.Linear(hidden_size , num_classes)
            if dr_rate:
                self.dropout = torch.nn.Dropout(p=dr_rate)
        
        def gen_attention_mask(self, token_ids, valid_length):
            attention_mask = torch.zeros_like(token_ids)
            for i, v in enumerate(valid_length):
                attention_mask[i][:v] = 1
            return attention_mask.float()

        def forward(self, token_ids, valid_length, segment_ids):
            attention_mask = self.gen_attention_mask(token_ids, valid_length)
            _, pooler = self.bert(input_ids = token_ids, token_type_ids = segment_ids.long(), attention_mask = attention_mask.float().to(token_ids.device))
            if self.dr_rate:
                out = self.dropout(pooler)
            return self.classifier(out)
    model = BERTClassifier(bertmodel,  dr_rate=0.5).to(device)

    print("MANAGE > 모델 인스턴스객체 로딩완료")
    main()
