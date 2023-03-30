<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;

class HealthyController extends AbstractController
{
    #[Route('/healthy', name: 'app_healthy')]
    public function index(): JsonResponse
    {
        return $this->json(['healthy' => 'ok'], Response::HTTP_OK);
    }
}
