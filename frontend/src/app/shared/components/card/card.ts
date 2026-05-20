import { Component, Input } from '@angular/core';
import { MatCardModule } from '@angular/material/card';

@Component({
	selector: 'fp-card',
	standalone: true,
	imports: [MatCardModule],
	templateUrl: './card.html',
	styleUrl: './card.scss'
})
export class CardComponent {
	@Input() title?: string;
	@Input() subtitle?: string;
}