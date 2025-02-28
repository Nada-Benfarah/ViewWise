import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-marketplace',
  imports: [ CommonModule,
    MatButtonModule],
  templateUrl: './marketplace.component.html',
  styleUrl: './marketplace.component.scss'
})
export class MarketplaceComponent {

  agents = [
    {
      name: 'Agent Builder',
      description: 'Un agent IA pour construire des projets complexes.',
      image: 'https://via.placeholder.com/300',
      rating: 4.5,
      price: '$29.99'
    },
    {
      name: 'Agent Assistant',
      description: 'Un assistant IA pour la gestion des tâches quotidiennes.',
      image: 'https://via.placeholder.com/300',
      rating: 4.2,
      price: '$19.99'
    },
    {
      name: 'Agent Analytique',
      description: 'Un agent IA pour l\'analyse de données et les rapports.',
      image: 'https://via.placeholder.com/300',
      rating: 4.7,
      price: '$39.99'
    },
    {
      name: 'Agent Créatif',
      description: 'Un agent IA pour la génération de contenu créatif.',
      image: 'https://via.placeholder.com/300',
      rating: 4.0,
      price: '$24.99'
    }
  ];
}
